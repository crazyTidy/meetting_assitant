"""LLM service for generating meeting summaries using ZhipuAI."""
import logging
import requests
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime

from ..settings.config import settings
from .separation_service import SpeakerInfo, SpeakerSegment
from .asr_service import TranscriptResult

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
        speaker_list = "、".join([s.display_name for s in speakers])

        prompt = f"""你是专业的公文写作助手。请根据以下会议转录内容生成一份公文标准格式的会议纪要。

【会议信息】
会议标题：{meeting_title}
参会人员：{speaker_list}

【会议转录内容】
{transcript.full_text}

【写作要求】
1. **内容提炼**：不要逐字逐句罗列转录内容，要对讨论进行提炼、归纳、总结
2. **按议题组织**：根据讨论内容归纳出若干主要议题，每个议题下概括核心观点和讨论要点
3. **引用发言**：重要观点可引用发言人并标注，如"张三指出：..."
4. **公文格式**：使用"一、二、三"作为大标题编号，使用"**标题**"加粗格式
5. **语言风格**：语言严谨、简洁、专业，避免口语化表达
6. **实事求是**：完全基于转录文本，不要虚构信息；未明确的信息填写"未明确提及"
7. **标题层级限制**：严格使用Markdown标题格式，最多使用####四级标题，禁止使用#####和######标题

【输出格式】
**会议时间**：[根据转录推断或填写"未明确提及"]
**会议地点**：[如转录中提到，请列出；否则写"未明确提及"]
**参会人员**：{speaker_list}
**记录人**：AI助手

---

**会议议题**：[一句话概括会议核心议题]

---

**会议内容**：

本次会议主要讨论了以下事项：

**一、[议题标题]**

[概括该议题的核心内容和讨论要点，提炼主要观点，如有重要发言请注明发言人]

**二、[议题标题]**

[概括该议题的核心内容和讨论要点]

**三、[议题标题]**

[概括该议题的核心内容和讨论要点]

---

**会议决议**：

一、[决议事项1]

二、[决议事项2]

三、[决议事项3]

[如无明确决议，可写"本次会议未形成明确决议"]

---

**会议要求**：（仅当会议中有明确的待办事项、任务分配时才输出此部分，否则删除）

一、[负责人/责任方]负责[具体事项]，于[时限]前完成。

二、[负责人/责任方]负责[具体事项]，于[时限]前完成。

---
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

            response = requests.post(api_url, headers=headers, json=payload, timeout=600)
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
        timeline: List[SpeakerSegment],
        speaker_name_map: Optional[dict] = None
    ) -> str:
        """Build prompt for meeting summary generation from timeline segments with transcripts."""

        # Build speaker info with speaking time
        speaker_list = "、".join([s.display_name for s in speakers])

        # Use display_name from map if available, otherwise use speaker_id
        def get_speaker_display_name(speaker_id: str) -> str:
            if speaker_name_map and speaker_id in speaker_name_map:
                return speaker_name_map[speaker_id]
            # Find in speakers list
            for s in speakers:
                if s.speaker_id == speaker_id:
                    return s.display_name
            return speaker_id

        # Build timeline as text with actual transcripts
        # Format: [timestamp] 显示名称 (speaker_id): 发言内容
        timeline_text = "\n".join([
            f"- [{self._format_timestamp(seg.start_time)}-{self._format_timestamp(seg.end_time)}] {get_speaker_display_name(seg.speaker_id)}: {seg.transcript if seg.transcript else '(暂无转写文本)'}"
            for seg in timeline
        ])

        prompt = f"""你是经验丰富的会议纪要专家，核心任务是：根据以下会议相关信息，生成一份**逻辑连贯、重点突出、符合实际场景**的正式会议纪要。

        【核心输入信息】
        - 会议核心标识：{meeting_title}（可作为标题/主题，也可根据发言调整为更精准的表述）
        - 相关参与方：{speaker_list}（可补充发言中提及的其他参与人，未提及则保持原样）
        - 原始素材：{timeline_text}（包括发言内容、讨论过程、相关补充信息等）

        【核心原则】
        1. 绝对忠实：所有内容100%基于原始素材，不虚构、不引申、不补充未提及信息；未明确的细节（如时间、地点、任务时限）统一标注“未明确提及”。
        2. 极致提炼：剔除口语化、重复、无关紧要的表述，保留核心观点、讨论分歧、关键建议、明确结论。
        3. 完全灵活：
        - 结构自适配：根据会议类型（例会/项目会/评审会/沟通会等）自主搭建框架，可分“议题-结论-任务”，也可分“讨论事项-达成共识-待办工作”，无需拘泥固定章节名；
        - 数量不强制：议题、结论、任务的数量完全由素材决定，1条或多条均可，不强行凑数；
        - 模块可取舍：有则写、无则删（如无任务分工则不出现“待办”模块，无明确结论则不出现“决议”模块，仅用一句话说明“本次会议未达成明确共识”）。
        4. 重点突出：关键意见、争议点、最终结论、需落地的事项要加粗或优先呈现；重要发言人的核心观点可标注姓名（如“XXX提出：XXX”），非关键观点可合并概括。
        5. 风格适配：根据会议场景调整文风——正式会议（公文严谨风）、商务会议（简洁高效风）、项目会议（务实落地风），无需统一刻板表述。

        【输出要求】
        - 标题明确：直接使用会议核心标识或优化后的精准标题（如“关于XX项目推进的会议纪要”）；
        - 逻辑清晰：段落/模块之间衔接自然，读者能快速get“讨论了什么-达成了什么-要做什么”；
        - 格式简洁：可使用序号、加粗、分点（不强制），避免复杂排版；
        - 语言得体：正式但不生硬，专业但不晦涩，适配会议的实际沟通场景。
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
        timeline: List[SpeakerSegment],
        speaker_name_map: Optional[dict] = None
    ) -> SummaryResult:
        """
        Generate meeting summary using Zhipu GLM based on timeline segments.

        This generates a summary structure based on speaker timeline without transcription.

        Args:
            audio_path: Path to audio file (for reference)
            speakers: List of speakers with metadata
            meeting_title: Title of the meeting
            timeline: List of speaker segments with timestamps
            speaker_name_map: Optional mapping from speaker_id to display_name

        Returns:
            SummaryResult with generated summary structure
        """
        logger.info(f"[LLM_SUMMARY] Generating summary from timeline for meeting: {meeting_title}")
        logger.info(f"[LLM_SUMMARY] API Key configured: {bool(self.api_key)}")
        logger.info(f"[LLM_SUMMARY] Number of speakers: {len(speakers)}")
        logger.info(f"[LLM_SUMMARY] Timeline segments: {len(timeline)}")

        try:
            # Build prompt for LLM
            prompt = self._build_prompt_from_timeline(meeting_title, speakers, timeline, speaker_name_map)

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

