"""Real-time transcription WebSocket endpoint."""
import json
import base64
import logging
import uuid
from datetime import datetime
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.meeting import Meeting, MeetingMode, MeetingStatus
from app.models.real_time_segment import RealTimeSegment
from app.services.whisperx_service import WhisperXTranscriber

logger = logging.getLogger(__name__)

router = APIRouter()

# Track active connections
active_connections: Dict[str, WebSocket] = {}
active_transcribers: Dict[str, WhisperXTranscriber] = {}


def get_db_session():
    """Get database session for WebSocket."""
    from app.core.database import AsyncSessionLocal
    return AsyncSessionLocal()


@router.websocket("/ws/transcribe")
async def transcribe_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time transcription."""
    await websocket.accept()
    logger.info("=" * 60)
    logger.info("🎤 新的 WebSocket 连接请求")

    meeting_id = None
    transcriber = None
    db = None
    audio_chunk_count = 0
    transcript_count = 0

    try:
        # Step 1: Receive initial handshake
        logger.info("📡 等待客户端握手消息...")
        init_data = await websocket.receive_json()
        logger.info(f"📨 收到握手消息: {init_data}")

        if init_data.get("type") != "init":
            logger.warning(f"❌ 握手消息类型错误: {init_data.get('type')}")
            await websocket.send_json({
                "type": "error",
                "message": "First message must be init"
            })
            await websocket.close()
            return

        meeting_id = init_data.get("meeting_id") or str(uuid.uuid4())
        language = init_data.get("language", "zh")
        title = init_data.get("title") or f"实时会议 {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        logger.info(f"🆔 会议ID: {meeting_id}")
        logger.info(f"📝 会议标题: {title}")
        logger.info(f"🌐 语言: {language}")

        # Step 2: Create meeting record
        logger.info("💾 创建会议记录...")
        db = get_db_session()
        meeting = Meeting(
            id=meeting_id,
            title=title,
            audio_path="",  # No file for real-time
            mode=MeetingMode.REAL_TIME,
            status=MeetingStatus.PROCESSING,
            progress=0,
            started_at=datetime.utcnow()
        )
        db.add(meeting)
        await db.commit()
        logger.info(f"✅ 会议记录已创建: {meeting_id}")

        # Step 3: Initialize transcriber
        logger.info("🔧 初始化转录服务...")
        transcriber = WhisperXTranscriber(meeting_id, language)
        await transcriber.initialize()
        logger.info("✅ 转录服务已初始化")

        active_connections[meeting_id] = websocket
        active_transcribers[meeting_id] = transcriber

        # Step 4: Send connected message
        logger.info("📤 发送连接确认消息...")
        await websocket.send_json({
            "type": "connected",
            "meeting_id": meeting_id,
            "message": "转录服务已就绪"
        })
        logger.info("✅ 连接确认已发送")

        # Step 5: Process audio stream
        logger.info("🎧 开始处理音频流...")
        logger.info("-" * 60)

        async for message in websocket.iter_json():
            msg_type = message.get("type")

            if msg_type == "audio":
                audio_chunk_count += 1
                audio_size = len(message.get("data", ""))
                logger.info(f"📦 [音频块 #{audio_chunk_count}] 大小: {audio_size} 字节")

                # Decode and process audio
                audio_data = base64.b64decode(message.get("data", ""))
                logger.info(f"🔓 [音频块 #{audio_chunk_count}] Base64解码完成，原始数据: {len(audio_data)} 字节")

                result = await transcriber.process_audio(audio_data)

                if result:
                    transcript_count += 1
                    logger.info(f"✨ [转录 #{transcript_count}] 说话人: {result['speaker']}")
                    logger.info(f"   📝 内容: {result['text']}")
                    logger.info(f"   ⏱️  时间: {result['start_time']}s - {result['end_time']}s")

                    # Save to database
                    segment = RealTimeSegment(
                        meeting_id=meeting_id,
                        speaker_id=result["speaker"],
                        text=result["text"],
                        start_time=result["start_time"],
                        end_time=result["end_time"],
                        is_final=True
                    )
                    db.add(segment)
                    await db.commit()
                    logger.info(f"💾 [转录 #{transcript_count}] 已保存到数据库，片段ID: {segment.id}")

                    # Send to frontend
                    await websocket.send_json({
                        "type": "transcript",
                        "data": {
                            "segment_id": segment.id,
                            "speaker": result["speaker"],
                            "text": result["text"],
                            "start_time": result["start_time"],
                            "end_time": result["end_time"]
                        }
                    })
                    logger.info(f"📤 [转录 #{transcript_count}] 已推送到前端")
                    logger.info("-" * 40)

            elif msg_type == "stop":
                logger.info("🛑 收到停止指令")
                break

    except WebSocketDisconnect as e:
        logger.warning(f"⚠️ WebSocket 连接断开: {e}")
    except Exception as e:
        logger.error(f"❌ WebSocket 错误: {e}", exc_info=True)
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass
    finally:
        # Cleanup
        logger.info("-" * 60)
        logger.info("🧹 开始清理资源...")

        if transcriber:
            await transcriber.cleanup()
            logger.info("✅ 转录服务已清理")

        if meeting_id:
            active_connections.pop(meeting_id, None)
            active_transcribers.pop(meeting_id, None)

            # Update meeting status
            if db:
                try:
                    meeting = await db.get(Meeting, meeting_id)
                    if meeting:
                        meeting.ended_at = datetime.utcnow()
                        meeting.status = MeetingStatus.COMPLETED
                        meeting.progress = 100
                        await db.commit()
                        logger.info(f"✅ 会议 {meeting_id} 状态已更新为完成")
                except Exception as e:
                    logger.error(f"❌ 更新会议状态时出错: {e}")

            if db:
                await db.close()
                logger.info("✅ 数据库连接已关闭")

        logger.info(f"📊 会议统计:")
        logger.info(f"   - 音频块总数: {audio_chunk_count}")
        logger.info(f"   - 转录条目数: {transcript_count}")
        logger.info("=" * 60)
        logger.info(f"🏁 会议 {meeting_id} 处理完成")
        logger.info("=" * 60)


@router.get("/transcribe/active")
async def get_active_sessions():
    """Get list of active transcription sessions."""
    logger.info(f"📋 查询活跃会话，当前数量: {len(active_connections)}")
    return {
        "active_sessions": list(active_connections.keys()),
        "count": len(active_connections)
    }
