# Top 6 Time Series Models
## 01. ARIMA Models
    Description 
        ARIMA 모델은 시간에 따라 수집된 데이터 포인트를 분석하고 추세(Trend) 및 계절성(Seasonality)과 같은 패턴을 파악하여 미래 가치를 예측
        안정적이고 선형적인 시계열에 가장 적합
    Examples 
        AR, MA, ARMA, ARIMA, SARIMA
    Workflow
        Collect data (데이터 수집)
        Clean & preprocess (정제 및 전처리)
        Check stationarity (정상성 확인)
        Difference the series (차분 - 정상성이 아닐 경우)
        Select parameters (p, d, q) (파라미터 선택)
        Train model (모델 학습)
        Validate forecast (예측 검증)
        Deploy (배포)

## 02. Exponential Smoothing Models
    Description 
        이 모델들은 최근 데이터에 더 많은 가중치를 부여하여 추세와 계절적 패턴이 있는 단기 예측에 효과적

    Examples
        Simple Exponential Smoothing, Holt's Linear Trend, Holt-Winters Seasonal

    Workflow:
        Load time series (시계열 로드)
        Detect trend/seasonality (추세/계절성 탐색)
        Choose smoothing method (평활화 방법 선택)
        Fit model (모델 적합)
        Adjust smoothing factors (평활 계수 조정)
        Generate forecast (예측 생성)
        Evaluate accuracy (정확도 평가)

## 03. Prophet Model
    Description
        Prophet은 Facebook에서 만든 유연하고 사용하기 쉬운 예측 모델임
        계절성, 추세, 휴일 및 누락된 데이터를 매우 잘 처리

    Examples
        일일 수요 예측, 웹사이트 트래픽, 판매 추세

    Workflow:
        Prepare data (데이터 준비)
        Define holidays/events (휴일/이벤트 정의)
        Fit Prophet model (Prophet 모델 적합)
        Inspect trend & seasonality (추세 및 계절성 점검)
        Refine parameters (파라미터 미세 조정)
        Forecast future values (미래 가치 예측)
        Visualize components (구성 요소 시각화)

## 04. LSTM Neural Networks
    Description
        LSTM은 시퀀스 데이터의 장기 의존성을 학습하도록 설계된 딥러닝 모델로, 복잡한 예측 작업에 이상적임

    Examples
        주가 예측, 에너지 소비, 기상 예보

    Workflow
        Collect sequence data (시퀀스 데이터 수집)
        Normalize (정규화)
        Transform to supervised format (지도 학습 형식으로 변환)
        Build LSTM layers (LSTM 레이어 구축)
        Train network (네트워크 학습)
        Predict future sequences (미래 시퀀스 예측)
        Evaluate performance (성능 평가)

## 05. VAR (Vector AutoRegression)
    Description
        VAR 모델은 서로 영향을 미치는 여러 시계열을 예측
        경제 지표, 카테고리별 매출 또는 다변량 예측에 적합함

    Examples
        GDP vs 인플레이션, 제품 카테고리 간 상호작용, 멀티 센서 판독값

    Workflow:
        Gather multiple time series (다중 시계열 수집)
        Check stationarity (정상성 확인)
        Select optimal lag (최적 시차 선택)
        Fit VAR model (VAR 모델 적합)
        Diagnose residuals (잔차 진단)
        Generate forecasts (예측 생성)
        Interpret variable interactions (변수 간 상호작용 해석)


## 06. Random Forest / Gradient Boosting for Time Series
    Description
        트리 기반 모델은 날짜를 특성(feature)으로 변환하여 시계열 예측을 수행할 수 있슴.
        관계가 비선형적이거나 많은 변수가 포함된 경우에 유용함.

    Examples
        XGBoost forecasting, LightGBM forecasting, Random Forest regression

    Workflow:
        Collect time-series data (시계열 데이터 수집)
        Create features (lags, rolling means, holidays) (특성 생성 - 시차, 이동 평균 등)
        Train model (모델 학습)
        Tune hyperparameters (하이퍼파라미터 튜닝)
        Predict (예측)
        Compare with baseline (기준 모델과 비교)
        Deploy (배포)


# 분석가가 알아야 할 20가지 통계지표
## 1. 기초 통계 지표 (기본 분포 및 산포)
    01. 평균 (Mean): 데이터 값들의 중앙 집중 경향 (공식: ∑x/n)
    02. 중앙값 (Median): 데이터를 상하 절반으로 나누는 중간값
    03. 최빈값 (Mode): 데이터 세트 내 가장 빈번하게 발생하는 값
    04. 표준편차 (Standard Deviation): 데이터가 평균으로부터 퍼져 있는 정도 (공식: ∑(x−μ)^2/n​)
    05. 분산 (Variance): 데이터 포인트들이 평균에서 벗어난 정도
    06. Z-점수 (Z-Score): 평균과 표준편차를 기준으로 데이터 포인트를 표준화한 수치

## 2. 회귀 및 예측 모델 성능 지표
    07. 상관계수 (Correlation Coefficient, r): 두 변수 간 관계의 강도와 방향 (범위: -1 ~ +1)
    08. 결정계수 (R-Squared, R2): 모델 예측값이 실제 데이터에 적합한 정도
    09. 평균 절대 오차 (MAE): 예측값과 실제값의 차이를 절대값으로 계산한 평균
    10. 평균 제곱 오차 (MSE): 예측값과 실제값 차이의 제곱에 대한 평균
    11. 평균 제곱근 오차 (RMSE): MSE의 제곱근으로 나타낸 예측 정확도
    12. 수정된 결정계수 (Adjusted R2): 예측 변수의 수를 고려하여 보정된 결정계수

## 3. 분류 모델 평가 지표
    13. 정밀도 (Precision): 양성 예측 중 실제 양성의 비율 (공식: TP/(TP+FP))
    14. 재현율 (Recall): 실제 양성 중 정확히 예측된 비율. (공식: TP/(TP+FN))
    15. F1-스코어 (F1-Score): 정밀도와 재현율의 조화 평균
    16. 정확도 (Accuracy): 전체 모델 예측의 올바른 비율 (공식: (TP+TN)/Total)
    17. 혼동 행렬 (Confusion Matrix): 실제값과 예측값의 분류 현황을 나타낸 표
    18. ROC-AUC 점수: 민감도와 특이도를 이용한 분류 성능 평가 수치

## 4. 통계적 가설 검정
    19.  P-값 (P-Value): 가설의 통계적 유의성 검정 지표
    20.  카이제곱 통계량 (Chi-Square Statistic): 범주형 변수 간의 관계 측정치


## 참고 : **Confusion matrix(참고)**
* 자극에 대한 반응을 하는 것은 자극(True/False) * 반응(Positive/Negative)의 2*2임. 
* 정밀도, 재현율, 정확도에 사용된 TP, FP등은 confusion matrix의 약어임. 
  
| 구분 | 예측: 양성 (P') | 예측: 음성 (N') |
| :-- | :--: | :--: |
| **실제: 양성 (P)** | **TP** (Truth) | **FN** (Miss) |
| **실제: 음성 (N)** | **FP** (False Alarm) | **TN** (Correct Negative) |
