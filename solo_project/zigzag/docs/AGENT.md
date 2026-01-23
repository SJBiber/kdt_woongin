# Zigzag 카테고리별 인기 상품 데이터 수집기 개발 착수서

## 1. 프로젝트 개요
사용자가 입력한 대항목 카테고리(예: 상의, 아우터 등)를 기준으로 지그재그(https://zigzag.kr)의 인기 순위 상품을 수집하고, 각 상품의 상세 정보 및 리뷰 데이터를 저장하는 자동화 시스템 구축.

## 2. 핵심 동작 프로세스 (Strict Workflow)
프로그램은 다음의 순서로만 동작하며, 예외적인 탐색을 최소화한다.

1.  **초기 입력**: 프로그램 실행 시 수집할 **대항목 카테고리명**을 입력받음 (User Input).
2.  **페이지 진입 및 이동**: 
    - 지그재그 메인 접속.
    - 카테고리 메뉴 진입 -> 입력받은 **대항목** (예: 상의, 팬츠) 탭 클릭.
3.  **정렬 설정**: 
    - 우측 정렬 필터를 클릭하여 **'인기순'**으로 변경.
4.  **상품 리스트 확보**: 
    - 화면에 로드된 상품들의 **브랜드명**, **상품명**, **상세 페이지 URL** 리스트를 1차 수집.
5.  **상세 데이터 수집 (Iterative Loop)**:
    - 각 상품 URL로 진입.
    - **단일 상품 정보**: 가격(정가/할인가), 총 리뷰 개수, 전체 평점, 대표 이미지 URL.
    - **리뷰 데이터**: **상품당 20개**의 리뷰 수집 (리뷰 본문, 해당 리뷰의 평점).
6.  **데이터 저장**: 
    - 수집된 데이터를 Supabase DB에 적재 (Product -> Review 관계 유지).

## 3. 데이터 스키마 설계 (Supabase)

### 3.1. Products Table (`zigzag_products`)
각 상품의 메타데이터를 저장한다.
| Column | Type | Notes |
| :--- | :--- | :--- |
| `id` | UUID | Primary Key |
| `category_major` | String | 입력받은 대항목 (예: 아우터) |
| `brand_name` | String | 스토어/브랜드명 |
| `product_name` | String | 상품명 |
| `final_price` | Integer | 최종 판매가 |
| `review_count` | Integer | 총 리뷰 수 |
| `rating_average` | Float | 평균 평점 (5.0 만점) |
| `image_url` | String | 상품 썸네일 URL |
| `product_url` | String | 상품 상세 링크 (Unique) |
| `collected_at` | Timestamp | 수집 일시 |

### 3.2. Reviews Table (`zigzag_reviews`)
상품별 수집된 20개의 리뷰 상세 데이터를 저장한다.
| Column | Type | Notes |
| :--- | :--- | :--- |
| `id` | UUID | Primary Key |
| `product_id` | UUID | Foreign Key -> `zigzag_products.id` |
| `content` | Text | 리뷰 내용 |
| `rating` | Integer | 개별 리뷰 평점 |
| `created_at` | Timestamp | 데이터 생성 일시 |

## 4. 기술 스택 및 제약 사항
-   **Language**: Python 3.12
-   **Browser Automation**: Playwright (필수: 동적 정렬 및 리뷰 팝업/스크롤링 처리)
-   **Database**: Supabase
-   **Constraint**: 불필요한 UI 탐색을 하지 않고, 지정된 정렬(인기순) 후 상위 아이템부터 순차적으로 처리한다.

## 5. 개발 단계 (Action Plan)
1.  **DB Setup**: Supabase에 위 2개 테이블 생성.
2.  **Scraper Logic (List)**: 카테고리 페이지 진입 -> 대항목 클릭 -> 인기순 정렬 -> 리스트 추출.
3.  **Scraper Logic (Detail)**: 상세 페이지 진입 -> 가격/이미지 추출 -> 리뷰 20개 로딩 및 추출.
4.  **Integration**: `main.py`에서 사용자 입력을 받아 전체 파이프라인 실행.
