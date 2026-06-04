from pydantic import BaseModel, Field

class ResumeDrftInput(BaseModel):
    selected_style: str = Field(..., description="Day2에서 고른 스타일")
    original_text: str = Field(..., description="개인정보를 제거한 원문")
    rewritten_text: str = Field(..., description="선택 스타일의 재작성 결과")
    observation: list[str] = Field(default_factory=list, description="관찰 메모")
    
draft = ResumeDrftInput(
    selected_style="스토리형",
    original_text=(
        "저는 맡은 일을 열심히 하는 사람입니다. "
        "FastAPI로 백엔드 프로젝트를 진행한 경험이 있고, "
        "팀원들과 협력해서 기능을 완성했습니다. "
        "입사 후 회사에 도움이 되는 개발자가 되겠습니다."
    ),
    rewritten_text=(
        "상황(S): FastAPI로 백엔드 프로젝트를 진행하며 팀원들과 협력하고 있는 상황입니다. "
        "과제(T): 일정 안에 기능을 완성하는 것이 중요했습니다. "
        "행동(A): FastAPI의 API 문서화를 자동화하여 팀원 간 상호 이해를 높였습니다. "
        "코드 리뷰 및 피드백 세션을 주기적으로 진행하여 상호 학습을 도모했습니다. "
        "결과(R): 예정된 일정 안에 기능을 완성했으며, 성능과 안정성 면에서 긍정적인 피드백을 받았습니다."
    ),
    observation=[
        "구조: STAR 4단계로 재구성됐지만 S/T/R에 구체적 정보가 부족해 흐름이 약하다.",
        "결함: 추상 표현(열심히, 도움이 되는), 수치 부재(기간/성과 없음), 직무 연결 약점(FastAPI 외 기술 언급 없음)",
        "키워드: FastAPI, 백엔드, API 문서화, 코드 리뷰, 협업",
        "STAR/PREP/CAR: STAR — S/T는 [추가 필요], A는 구체적, R은 수치 없음",
        "재작성 후보: '팀원들과 협력해서 기능을 완성했습니다.' → 행동(A)으로 구체화 가능성이 가장 높은 문장",
    ],
)

print(draft.model_dump())