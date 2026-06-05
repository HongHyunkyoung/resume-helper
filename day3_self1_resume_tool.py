from pydantic import BaseModel, Field
from enum import Enum

class DefectType(str, Enum):
    abstract_expression = "추상표현"
    missing_metric = "정량부재"
    keyword_mismatch = "키워드미스매치"
    self_promotion = "자기자랑"
    inconsistency = "일관성결여"
    generic_template = "공통템플릿"

class ResumeAnalysis(BaseModel):
    growth: str = Field(..., description="성장 과정 분석")
    motivation: str = Field(..., description="지원 동기 분석")
    aspiration: str = Field(..., description="입사 후 포부 분석")
    experience: str = Field(..., description="직무 경험 분석")
    success_failure: str = Field(..., description="성공/실패 경험 분석")
    
    
# ── 예시 JSON 스캐폴드 ──────────────────────────────────────
# 실제 API 호출 결과가 아니라 "어떤 값이 들어갈지" 형태만 보는 자료다.
# 개인정보를 넣지 않는다.

SAMPLE_JSON = {
    "growth": "FastAPI 프로젝트를 통해 백엔드 개발 역량을 쌓았으나 직무 연결 근거가 부족함",
    "motivation": "지원 동기 관련 내용이 샘플에 없어 확인 불가",
    "aspiration": "입사 후 포부 관련 내용이 샘플에 없어 확인 불가",
    "experience": "로그인 API 구현 및 오류 로그 분석 경험이 있으나 수치·기간 없음",
    "success_failure": "응답 시간 개선 시도가 있으나 결과 수치와 배운 점이 드러나지 않음",
}

def build_sample_payload() -> dict:
    """SAMPLE_JSON을 기반으로 검증용 딕셔너리를 반환한다."""
    return SAMPLE_JSON

def validate_payload() -> None:
    """ResumeAnalysis.model_validate()로 필드 누락을 점검한다."""
    payload = build_sample_payload()
    try:
        result = ResumeAnalysis.model_validate(payload)
        print("검증 성공")
        print("필드 목록:", list(result.model_fields.keys()))
    except Exception as e:
        print("검증 실패:", e)

if __name__ == "__main__":
    validate_payload()
    
    schema = ResumeAnalysis.model_json_schema()
    print("스키마 필드:", list(schema["properties"].keys()))
    
    