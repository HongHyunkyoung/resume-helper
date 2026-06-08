import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

MODEL_OPENAI = os.getenv("MODEL_OPENAI", "gpt-4o-mini")

CHECK_ITEMS =[
    "STAR 구조 충족 여부",
    "정량 근거 포함 여부",
    "NCS 직무 키워드 밀도",
]

def check_resume_ai_filter(resume_text: str, check_items:list[str]) -> str:
    """선택한 검증 항목을 기준으로 자소서를 점검한다"""

    system_prompt = (
        "당신은 AI 1차 필터 역할을 하는 자소서 점검 도우미입니다.\n"
        "검증 항목을 기준으로 자소서를 점검하고, 개선 권고를 1개 이상 제시하세요.\n"
        f"검증 항목: {', '.join(check_items)}"
    )

    response = client.chat.completions.create(
        model=MODEL_OPENAI,
        max_completion_tokens=700,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": resume_text},
        ],
    )

    return response.choices[0].message.content

BLIND_RISK_WORDS = [
    "나이",
    "살",
    "학교",
    "대학교",
    "대학원",
    "학점",
    "출신",
    "지역",
    "주소",
    "사진",
    "성별",
    "남자",
    "여자",
    "가족",
    "부모",
]

def check_blind_risks(resume_text:str) ->list[str]:
    """블라인드 채용 위험 표현 후보를 찾는다."""
    found = []
    for word in BLIND_RISK_WORDS:
        if word in resume_text:
            found.append(word)
    return found

def format_blind_report(found: list[str]) -> str:
    """위험 표현 후보를 사람이 읽기 쉬운 문장으로 바꾼다."""
    if not found:
        return "블라인드 채용 위험 표현 후보가 발견되지 않았어요."
    
    lines = ["블라인드 채용 위험 표현 후보:"]
    for word in found:
        lines.append(f"  - '{word}' 발견 -> 제거 또는 수정을 권장합니다.")
    return "\n".join(lines)



if __name__ == "__main__":
    print("선택한 검증 항목:")
    for item in CHECK_ITEMS:
        print("-", item)

    sample_text = """
    FastAPI를 활용해 로그인 API를 구현했습니다.
    오류 로그를 분석해 재발 방지 문서를 만들었고,
    팀원들과 코드 리뷰를 통해 완성도를 높였습니다.
    입사 후 회사에 도움이 되는 개발자가 되겠습니다.
    """

    print("\n[AI 1차 필터 점검 결과]")
    result = check_resume_ai_filter(sample_text, CHECK_ITEMS)
    print(result)
    print("\n[/blind 점검 결과]")
    blind_sample = "OO대학교를 졸업하고 지원합니다. 나이는 25살입니다."
    found = check_blind_risks(blind_sample)
    print(format_blind_report(found))
