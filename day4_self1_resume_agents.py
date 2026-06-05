# day4_self1_resume_agents.py
# Day 4 self1 — 분석 Agent + Triage 라우팅

import os
import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner

load_dotenv()

def check_env() -> None:
    """OPENAI_API_KEY 존재 여부만 확인한다. 키 원문은 출력하지 않는다."""
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print("OPENAI_API_KEY 로딩 확인")
    else:
        print("OPENAI_API_KEY를 .env에 먼저 넣어주세요.")
        
if __name__  == "__main__":
    check_env()
    
analyze_agent = Agent(
     name="ResumeAnalyzeAgent",
     handoff_description="자소서 분석, ResumeAnalysis 5필드, 6대 결함 탐지 요청을 담당한다.",
        instructions="""
        당신은 한국 채용 맥락을 이해하는 자소서 분석 전문가입니다.
    사용자가 입력한 자소서 원문을 읽고 아래 기준으로 분석 결과를 한국어로 출력합니다.
    첨삭 문장을 직접 작성하지 않습니다. 분석과 결함 태그에 집중합니다.

    [분석 기준 — ResumeAnalysis 5필드]
    - 성장: 성장 과정이 지원 직무와 연결되는지 확인한다.
    - 동기: 지원 동기가 회사·직무와 구체적으로 연결되는지 확인한다.
    - 포부: 입사 후 포부가 행동 단위로 서술됐는지 확인한다.
    - 경험: STAR 구조(상황-과제-행동-결과)로 설명할 경험이 있는지 확인한다.
    - 성공실패: 성공 또는 실패에서 배운 점이 드러나는지 확인한다.

    [결함 점검 — 6대 결함]
    - 추상적 표현: "열심히", "최선을", "좋은" 같은 표현만 있는지 확인한다.
    - 수치 부재: 기간, 성과, 규모, 결과 수치가 없는지 확인한다.
    - 복붙 흔적: 어느 회사에 넣어도 같은 문장인지 확인한다.
    - 직무 불일치: 지원 직무와 관련 없는 경험이 주를 이루는지 확인한다.
    - NCS 미반영: 직무 키워드가 자소서에 반영됐는지 확인한다.
    - 블라인드 위반: 학교명, 나이, 성별, 지역 같은 개인정보 표현이 있는지 확인한다.

    출력은 5필드 분석 요약과 발견된 결함 태그 목록 중심으로 작성합니다.
    """,
    )

triage_agent = Agent(
    name="ResumeTriageAgent",
    instructions="""
    당신은 자소서 도우미의 접수 담당입니다.
    사용자 요청을 읽고 적합한 전문가에게 넘기는 역할만 합니다.
    직접 긴 분석이나 첨삭 문장을 작성하지 않습니다.

    [라우팅 규칙]
    - 자소서 분석, ResumeAnalysis 5필드 확인, 결함 탐지 요청
    → 분석 전문가(ResumeAnalyzeAgent)에게 넘긴다.

    - 첨삭, 최종본 생성, Guardrails 요청
    → "해당 기능은 다음 단계에서 추가될 예정입니다."라고 짧게 안내한다.

    - 날씨, 잡담, 자소서와 관련 없는 요청
    → "자소서 도우미의 범위 밖 요청입니다."라고 짧게 안내한다.
    """,
    handoffs=[analyze_agent],
)

TEST_CASES = [
    {
        "label": "분석 요청",
        "input": """
        아래 자소서를 ResumeAnalysis 5필드 기준으로 분석해줘.
        저는 팀 프로젝트에서 로그인 API 오류를 정리했고,
        재발 방지를 위해 오류 메시지와 테스트 케이스를 문서화했습니다.
        입사 후 회사에 도움이 되는 개발자가 되겠습니다.
        """    
    },
    {
        "label":"범위 밖 요청",
        "input": "오늘 서울 날씨가 어때?",
    },
]

async def run_case(label: str, user_input: str) -> dict:
    """Triage를 실행하고 라우팅 결과를 반환한다."""
    print(f"\n---{label}---")
    
    result = await Runner.run(triage_agent, input=user_input)
    
    last_agent = result.last_agent.name
    output_preview = str(result.final_output)[:200]
    
    print(f"last_agent: {last_agent}")
    print(f"output: {output_preview}")
    
    return {
        "label": label,
        "last_agent": last_agent,
        "output_preview": output_preview,    
    }
    
async def main() -> None:
    """테스트 케이스를 순서대로 실행한다."""
    logs = []
    for case in TEST_CASES:
        log = await run_case(case["label"], case["input"])
        logs.append(log)
    # 라우팅 결과 요약 출력
    print("\n\n===라우팅 요약===")
    for log in logs:
        print(f"{log['label']} -> {log['last_agent']}")
        
        
if __name__ == "__main__":
    check_env()
    asyncio.run(main())
    