from pathlib import Path
from pydantic import BaseModel, Field


class ResumeAnalysis(BaseModel):
    score: int = Field(ge=0, le=100, description="종합 분석 점수 (0~100)")
    defects: list[str] = Field(default_factory=list, description="발견된 결함 목록")
    keyword_match: dict = Field(default_factory=dict, description="키워드 매칭 결과")
    blind_violations: list[str] = Field(default_factory=list, description="블라인드 채용 위험 목록")
    revised_text: str = Field(default="", description="수정 방향 또는 재작성 결과")
    
def normalize_keywords(raw_keywords: str) -> list[str]:
    """쉼표로 구분된 키워드 문자열을 리스트로 변환한다."""
    return [kw.strip() for kw in raw_keywords.split(",") if kw.strip()]

def match_keywords(resume_text:str, required_keywords: list[str]) -> dict:
    """
    자소서 원문에서 필수 키워드 매칭 여부를 확인한다.
    반환: required, matched, missing, score
    """
    matched = [kw for kw in required_keywords if kw in resume_text]
    missing = [kw for kw in required_keywords if kw not in resume_text]
    
    total = len(required_keywords)
    score = round(len(matched) / total * 100, 1) if total > 0 else 0.0
    
    return {
        "required": required_keywords,
        "matched": matched,
        "missing": missing,
        "score": score,
    }
    
def detect_blind_violations(resume_text: str) -> list[str]:
    """
    블라인드 채용에서 위험한 표현 패턴을 탐지한다.
    실제 개인정보를 예시로 쓰지 않는다.
    """
    violations: list[str] = []
    
    risky_patterns = [
        ("대학교", "학교명 또는 학력 직접 노출"),
        ("학점", "학점 직접 노출"),
        ("나이", "나이 직접 노출"),
        ("살이에요", "나이 직접 노출"),
        ("남자", "성별 직접 노출"),
        ("여자", "성별 직접 노출"),
        ("출신", "지역 또는 출신 직접 노출"),
    ]
    
    for pattern, label in risky_patterns:
        if pattern in resume_text:
            violations.append(label)
            
    return violations

def detect_flaws(resume_text: str, required_keywords: list[str]) -> list[str]:
    """
    자소서 원문에서 6대 결함을 탐지한다.
    규칙 기반으로 시작하고, 완벽하지 않아도 된다.
    """
    defects: list[str] = []
    
    # 결함 1 — STAR/PREP 프레임 미준수
    # 상황, 과제, 행동, 결과, 근거 중 하나도 없으면 결함으로 본다
    star_keywords = ["상황", "과제", "행동", "결과", "근거", "이유", "때문에"]
    if not any(kw in resume_text for kw in star_keywords):
        defects.append("STAR/PREP 프레임 미준수")
        
    # 결함 2 — NCS 키워드 누락
    # match_keywords에서 missing이 있으면 결함으로 본다
    kw_result = match_keywords(resume_text, required_keywords)
    if kw_result["missing"]:
        defects.append("NCS 키워드 누락")
        
    # 결함 3 — 블라인드 채용 위반
    blind = detect_blind_violations(resume_text)
    if blind:
        defects.append("블라인드 채용 위반")
    
    # 결함 4 — 공백 문장
    # 마침표로 나눴을 때 빈 문장이 있으면 결함으로 본다
    sentences = [s.strip() for s in resume_text.split(".")]
    if any(s == "" for s in sentences):
        defects.append("공백 문장")
        
    # 결함 5 — 일반화 표현
    generic_words = ["최선을", "열심히", "좋은", "훌륭한", "성실히"]
    if any(word in resume_text for word in generic_words):
        defects.append("일반화 표현")
        
    # 결함 6 — 수동태 남발
    # "되었습니다", "됩니다"가 2번 이상 반복되면 결함으로 본다
    passive_count = resume_text.count("되었습니다") + resume_text.count("됩니다")
    if passive_count >=2:
        defects.append("수동태 남발")
        
    return defects
    
def analyze_resume(resume_text: str, raw_keywords: str) -> ResumeAnalysis:
    """
    자소서 원문과 키워드를 받아 ResumeAnalysis를 반환한다.
    API 호출 없이 로컬 함수로만 동작한다.
    """
    # 1. 키워드 정규화
    keywords = normalize_keywords(raw_keywords)
    
    # 2. 키워드 매칭
    kw_result = match_keywords(resume_text, keywords)
    
    # 3. 블라인드 위험 탐지
    blind = detect_blind_violations(resume_text)
    
    # 4. 6대 결함 탐지
    defects = detect_flaws(resume_text, keywords)
    
    # 5. 점수 계산(키워드 매칭 점수 기반, 결함 수만큼 감점)
    base_score = int(kw_result["score"])
    penalty = len(defects) * 10
    score = max(0, base_score - penalty)
    
    # 6. 수정 방향 (간다한 안내 문자열)
    revised_text = f"발견된 결함{len(defects)}개: {', '.join(defects)}"
    
    payload = {
        "score": score,
        "defects": defects,
        "keyword_match": kw_result,
        "blind_violations": blind,
        "revised_text": revised_text,
    }
    
    return ResumeAnalysis.model_validate(payload)

def save_analysis(analysis: ResumeAnalysis, output_path: str ="analyze_result.json") -> None:
    """분석 결과를 UTF-8 JSON 파일로 저장한다."""
    path = Path(output_path)
    path.write_text(analysis.model_dump_json(indent=2), encoding="utf-8")
    print(f"저장 위치: {path.resolve()}")
    print(f"분석 점수: {analysis.score}")
    print(f"결함 수: {len(analysis.defects)}")
    
def run_cli() -> None:
    """자소서 도우미 CLI 진입점."""
    print("자소서 도우미입니다. /analyze 를 입력하세요.")
    command = input("명령: ").strip()
    
    if command == "/analyze":
        resume_text = input("자소서 원문: ").strip()
        raw_keywords = input("NCS/JD 키워드 (쉼표 구분): ").strip()
        
        if not resume_text:
            print("자소서 원문이 비어 있습니다.")
            return
        
        analysis = analyze_resume(resume_text, raw_keywords)
        save_analysis(analysis)
        print("\n[분석 완료]")
        print(f"score: {analysis.score}")
        print(f"defects: {analysis.defects}")
        
    else:
        print("지원하는 명령: /analyze")
        
if __name__ == "__main__":
    run_cli()