# 8주차 회고 — 나만의 자소서 도우미

## Day 1
- 배운 것: .env와 python-dotenv로 API 키를 관리하고 OpenAI 첫 호출 구조를 익혔다.

## Day 2
- 배운 것: PCT 구조로 /style 프리셋을 설계하고 스타일별 system 프롬프트를 분리했다.

## Day 3
- 배운 것: Pydantic BaseModel로 ResumeAnalysis 5필드를 정의하고 6대 결함을 코드화했다.

## Day 4
- 배운 것: Triage Agent가 Specialist로 라우팅하는 멀티에이전트 구조와 Guardrails를 구현했다.

## Day 5
- 배운 것: AI 1차 필터 관점으로 자소서를 검증하고 /blind 블라인드 채용 점검 기능을 추가했다.

## PE 기법 정리
- PCT 구조: Persona/Context/Task로 프롬프트를 나눠 역할을 명확히 했다.
- 프롬프트 인젝션 방어: Agent instructions에 역할 재정의 거부 문구를 넣었다.
- Structured Output: Pydantic으로 ResumeAnalysis 스키마를 고정해 결과를 구조화했다.
- 스타일 차별화: 간결형/스토리형/직무맞춤형/수치강조형/지원동기형 5종으로 프롬프트를 분리했다.