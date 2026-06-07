import os
from dotenv import load_dotenv
from openai import OpenAI
from styles import STYLE_PRESETS, list_style_names
from day5_self1_resume_pipeline import check_blind_risks, format_blind_report

load_dotenv()

RESUME_SYSTEM_PROMPT = """
    너는 한국 채용 맥락을 이해하는 자소서 첨삭 전문가입니다.
    사용자가 입력한 자기소개서 또는 지원동기를 읽고,
    구체적인 개선 방향을 한국어로 제안합니다.

    [첨삭 기준]
    1. 추상적 표현 탐지: "열심히", "노력", "성장하고 싶다" 같은 표현은 구체적 사례로 바꾸도록 안내해.
    2. STAR 구조 확인: 상황(S) - 과제(T) - 행동(A) - 결과(R) 흐름이 있는지 봐줘.
    3. 직무 키워드 확인: 지원 직무와 관련된 단어가 있는지 확인해.
    4. 정량 지표 확인: 숫자나 구체적 성과가 없는 문장은 추가를 권유해.
    5. 블라인드 채용 주의: 학교명, 지역, 가족 정보 등 드러나는 표현을 지적해.
    """

def get_sample_resume() -> str:
    # TODO: 본인 자소서가 없으면 대체 샘플 1개를 반환해요.
    return """
    저는 맡은 일을 열심히 하는 사람입니다.
    백엔드 개발자로 성장하고 싶고, 프로젝트에서도 책임감 있게 참여했습니다.
    입사 후 회사에 도움이 되는 개발자가 되겠습니다.
    """

def load_settings() -> dict:
    openai_key = os.environ.get("OPENAI_API_KEY")
    return {
        "openai_key_exists": openai_key is not None
    }

def ask_openai_once(sample_text: str) -> str:
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_completion_tokens=1000,
        messages=[
            {"role": "system", "content": RESUME_SYSTEM_PROMPT},
            {"role": "user", "content":sample_text}
        ]
    )
    return response.choices[0].message.content

def handle_style_command(user_input: str, current_key: str) -> str:
    """
    /style 명령을 처리하고 선택된 스타일 키를 반환한다.
    스타일 이름이 없거나 잘못됐으면 현재 키를 그대로 반환한다.
    """
    parts = user_input.split(maxsplit=1)
    
    # /style만 입력했을 때
    if len(parts) < 2:
        print(f"사용 가능한 스타일: {list_style_names()}")
        print(f"현재 스타일: {current_key}")
        return current_key
    
    style_key = parts[1].strip()
    
    if style_key in STYLE_PRESETS:
        print(f"스타일 변경: {current_key} -> {style_key}")
        return style_key
    
    print(f"'{style_key}'는 없는 스타일입니다.")
    print(f'사용 가능한 스타일: {list_style_names()}')
    return current_key
   
def chat_loop() -> None:
    print("자소서 도우미를 시작합니다. /help로 도움말, /quit으로 종료합니다.")
    print(f"현재 스타일: 간결형 | 변경: /style [스타일명]")
    
    client = OpenAI()
    current_style_key = "간결형"
    
    while True:
        user_input = input("자소서 입력 > ").strip()
        
        if user_input == "/help":
            print("""
            [자소서 도우미 사용 방법]
            - 자소서 문단을 붙여넣고 Enter를 누르면 첨삭 피드백을 받아요.
            - /style [스타일명] : 첨삭 스타일을 바꿔요. (간결형, 스토리형, 직무맞춤형)
            - /style : 사용 가능한 스타일 목록을 봐요.
            - /help : 이 도움말을 다시 볼 수 있어요.
            - /quit : 프로그램을 종료해요.
            - /blind : 블라인드 채용 위험 표현을 점검해요.
            - 이름, 학교, 연락처 같은 개인정보는 입력하지 마세요.
            """)
            continue
        
        elif user_input == "/quit":
            print("자소서 도우미를 종료합니다.")
            break
        elif user_input == "/blind":  
            resume_text = input("점검할 자소서를 붙여넣으세요 > ").strip()
            if not resume_text:
                print("자소서 내용을 입력해주세요.")
                continue
            found = check_blind_risks(resume_text)
            print(format_blind_report(found))
            continue

        elif user_input.startswith("/style"):
            current_style_key = handle_style_command(user_input, current_style_key)
            continue
                
        elif not user_input:
            print("자소서 내용을 입력해주세요.")
            continue

        
        # 선택된 스타일의 system 프롬프트 가져오기
        system_prompt = STYLE_PRESETS[current_style_key]["system"]
        style_name = STYLE_PRESETS[current_style_key]["name"]
        print(f"\n[{style_name}으로 첨삭 중 ...]")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_completion_tokens=700,
            messages=[
                {"role":"system", "content": system_prompt},
                {"role":"user", "content":user_input}
            ]
        )
        
        answer = response.choices[0].message.content
        print("\n[첨삭 결과]")
        print(answer)
        print()

        


if __name__ == "__main__":
    chat_loop()