"""LLM service for generating meeting summaries using ZhipuAI."""
import logging
import requests
from typing import List, Optional
from dataclasses import dataclass

from app.core.config import settings
from app.services.separation_service import SpeakerInfo, SpeakerSegment
from app.services.asr_service import TranscriptResult

logger = logging.getLogger(__name__)


@dataclass
class SummaryResult:
    """Result from summary generation."""
    content: str  # Markdown formatted summary
    raw_response: Optional[str] = None


class LLMService:
    """Service for generating meeting summaries using Zhipu GLM."""

    def __init__(self):
        self.api_key = settings.ZHIPU_API_KEY
        self.api_key = "dc27759f5b5a4107b6af67aaf60e4a23.DmhTXSW9nk0eL74y"

    def _build_prompt(
        self,
        meeting_title: str,
        speakers: List[SpeakerInfo],
        transcript: TranscriptResult
    ) -> str:
        """Build prompt for meeting summary generation with full transcript."""

        # Build speaker info with speaking time
        speaker_list = "\n".join([
            f"- {s.display_name} ({s.speaker_id}) - 发言时长: {int(s.total_duration/60)}分{int(s.total_duration%60)}秒"
            for s in speakers
        ])

        prompt = f"""请根据以下会议信息和完整转录内容生成一份详细的会议纪要。

会议标题：{meeting_title}

参会人员：
{speaker_list}

会议转录内容：
{transcript.full_text}

请按照以下格式生成会议纪要（使用Markdown格式）：

## 会议主题
[简要描述会议的主要议题，基于转录内容提炼]

## 主要议题
1. [议题1 - 从转录中识别]
2. [议题2 - 从转录中识别]
3. [议题3 - 从转录中识别]

## 讨论要点
[按议题分类列出讨论的主要内容，引用关键发言]

### 议题1：[标题]
- [说话人X]：[关键观点或发言摘要]
- [说话人Y]：[回应或补充]

### 议题2：[标题]
- [说话人X]：[关键观点]
- ...

## 决议事项
- [基于讨论内容总结的决议1]
- [决议2]

## 待办事项
- [ ] [负责人]：[具体任务] - [截止日期（如转录中提到）]
- [ ] [负责人]：[具体任务]

## 下次会议安排
[如转录中提到下次会议计划，请列出时间和议题]

请确保：
1. 内容完全基于转录文本，不要虚构信息
2. 准确引用发言人的观点
3. 保持专业、简洁、重点突出
4. 如果转录中没有明确提到某个部分（如待办事项），可以标注"未明确讨论"
"""

        return prompt

    async def generate_summary(
        self,
        audio_path: str,
        speakers: List[SpeakerInfo],
        meeting_title: str,
        transcript: TranscriptResult
    ) -> SummaryResult:
        """
        Generate meeting summary using Zhipu GLM based on transcript.

        This calls the Zhipu AI API to generate meeting summaries.

        Args:
            audio_path: Path to audio file (for reference)
            speakers: List of speakers with metadata
            meeting_title: Title of the meeting
            transcript: Complete transcript with timeline

        Returns:
            SummaryResult with generated summary
        """
        logger.info(f"[LLM_SUMMARY] Generating summary for meeting: {meeting_title}")
        logger.info(f"[LLM_SUMMARY] API Key configured: {self.api_key}")
        logger.info(f"[LLM_SUMMARY] Number of speakers: {len(speakers)}")
        logger.info(f"[LLM_SUMMARY] Transcript segments: {len(transcript.segments)}")
        logger.info(f"[LLM_SUMMARY] Full text length: {len(transcript.full_text)} characters")

        try:
            # Build prompt for LLM
            prompt = self._build_prompt(meeting_title, speakers, transcript)

            # Print the full prompt for debugging
            logger.info(f"[LLM_SUMMARY] === PROMPT START ===")
            logger.info(f"[LLM_SUMMARY] {prompt}")
            logger.info(f"[LLM_SUMMARY] === PROMPT END ===")
            logger.info(f"[LLM_SUMMARY] Prompt length: {len(prompt)} characters")

            # Real API call to Zhipu AI (智谱 GLM) using requests
            logger.info(f"[LLM_SUMMARY] Calling Zhipu AI API...")

            api_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "glm-4-flash",
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的会议纪要助手，擅长从会议转录中提炼关键信息。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }

            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            response_data = response.json()

            logger.info(f"[LLM_SUMMARY] API response received, id: {response_data.get('id')}")
            logger.debug(f"[LLM_SUMMARY] Response model: {response_data.get('model')}")
            logger.debug(f"[LLM_SUMMARY] Usage: {response_data.get('usage')}")

            content = response_data['choices'][0]['message']['content']
            raw_response = str(response_data)

            logger.info(f"[LLM_SUMMARY] Summary generated successfully")
            logger.info(f"[LLM_SUMMARY] Summary length: {len(content)} characters")

            return SummaryResult(
                content=content,
                raw_response=raw_response
            )

        except requests.RequestException as e:
            logger.error(f"[LLM_SUMMARY] API request failed: {e}")
            raise
        except KeyError as e:
            logger.error(f"[LLM_SUMMARY] Invalid API response format: {e}")
            raise
        except Exception as e:
            logger.exception(f"[LLM_SUMMARY] Error generating summary: {e}")
            raise

    def _build_prompt_from_timeline(
        self,
        meeting_title: str,
        speakers: List[SpeakerInfo],
        timeline: List[SpeakerSegment]
    ) -> str:
        """Build prompt for meeting summary generation from timeline segments with transcripts."""

        # Build speaker info with speaking time
        speaker_list = "\n".join([
            f"- {s.display_name} ({s.speaker_id}) - 发言时长: {int(s.total_duration/60)}分{int(s.total_duration%60)}秒"
            for s in speakers
        ])

        # Build timeline as text with actual transcripts
        timeline_text = "\n".join([
            f"- [{self._format_timestamp(seg.start_time)}-{self._format_timestamp(seg.end_time)}] {seg.speaker_id}: {seg.transcript if seg.transcript else '(暂无转写文本)'}"
            for seg in timeline
        ])

        prompt = f"""请根据以下会议信息和完整发言记录生成一份会议纪要。

会议标题：{meeting_title}

参会人员：
{speaker_list}

发言记录（按时间顺序）：
{timeline_text}

请按照以下格式生成会议纪要（使用Markdown格式）：

## 会议主题
[从讨论内容提炼会议主题]

## 参会人员
{speaker_list}

## 主要议题
[基于发言内容识别的主要议题，按重要性排序]

## 讨论要点
[按议题分类整理，引用关键发言]

### 议题1：[标题]
- [说话人A]：[观点或发言摘要]
- [说话人B]：[回应或补充]

### 议题2：[标题]
- [说话人A]：[关键观点]
- [说话人B]：[补充说明]

## 决议事项
- [基于讨论内容总结的决议]
- [达成的共识]

## 待办事项
- [ ] [负责人]：[具体任务] - [截止日期（如提到）]

## 下次会议安排
[如提到下次会议，请列出时间和议题]

请确保：
1. 完全基于提供的发言记录内容生成纪要
2. 准确引用和归纳发言人的观点
3. 保持客观、简洁、重点突出
4. 如果某些部分（如待办事项）没有明确提到，标注"未明确讨论"
"""

        return prompt

    def _format_timestamp(self, seconds: float) -> str:
        """Format timestamp as MM:SS."""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    async def generate_summary_from_timeline(
        self,
        audio_path: str,
        speakers: List[SpeakerInfo],
        meeting_title: str,
        timeline: List[SpeakerSegment]
    ) -> SummaryResult:
        """
        Generate meeting summary using Zhipu GLM based on timeline segments.

        This generates a summary structure based on speaker timeline without transcription.

        Args:
            audio_path: Path to audio file (for reference)
            speakers: List of speakers with metadata
            meeting_title: Title of the meeting
            timeline: List of speaker segments with timestamps

        Returns:
            SummaryResult with generated summary structure
        """
        logger.info(f"[LLM_SUMMARY] Generating summary from timeline for meeting: {meeting_title}")
        logger.info(f"[LLM_SUMMARY] API Key configured: {bool(self.api_key)}")
        logger.info(f"[LLM_SUMMARY] Number of speakers: {len(speakers)}")
        logger.info(f"[LLM_SUMMARY] Timeline segments: {len(timeline)}")

        try:
            # Build prompt for LLM
            prompt = self._build_prompt_from_timeline(meeting_title, speakers, timeline)

            # Print the full prompt for debugging
            logger.info(f"[LLM_SUMMARY] === TIMELINE PROMPT START ===")
            logger.info(f"[LLM_SUMMARY] {prompt}")
            logger.info(f"[LLM_SUMMARY] === TIMELINE PROMPT END ===")
            logger.info(f"[LLM_SUMMARY] Prompt length: {len(prompt)} characters")

            # Real API call to Zhipu AI (智谱 GLM) using requests
            logger.info(f"[LLM_SUMMARY] Calling Zhipu AI API...")

            api_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "glm-4-flash",
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的会议纪要助手，擅长根据会议时间轴生成结构化纪要。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }

            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            response_data = response.json()

            logger.info(f"[LLM_SUMMARY] API response received, id: {response_data.get('id')}")
            logger.debug(f"[LLM_SUMMARY] Response model: {response_data.get('model')}")
            logger.debug(f"[LLM_SUMMARY] Usage: {response_data.get('usage')}")

            content = response_data['choices'][0]['message']['content']
            raw_response = str(response_data)

            logger.info(f"[LLM_SUMMARY] Summary generated successfully from timeline")
            logger.info(f"[LLM_SUMMARY] Summary length: {len(content)} characters")

            return SummaryResult(
                content=content,
                raw_response=raw_response
            )

        except requests.RequestException as e:
            logger.error(f"[LLM_SUMMARY] API request failed: {e}")
            raise
        except KeyError as e:
            logger.error(f"[LLM_SUMMARY] Invalid API response format: {e}")
            raise
        except Exception as e:
            logger.exception(f"[LLM_SUMMARY] Error generating summary from timeline: {e}")
            raise


# Singleton instance
llm_service = LLMService()

