# Text mining with MongoDB
서강대학교 데이터베이스 시스템(CSE4110) 프로젝트#3의 제출물

## 목적

1. 프로젝트 제출물 아카이빙
2. PEP8을 적용해 코드 다듬기
3. 간단한 리팩토링

## 문제 정의

본 프로젝트에서는 텍스트 마이닝 기법 중 하나인 **Apriori Algorithm**을 이요하여 제공된 뉴스 기사들을 분석하고 뉴스 기사에서 주로 쓰이는 단어들을 알아내는 프로그램을 작성한다. 또한 뉴스 기사 분석을 위해 비정형 데이터를 다루기 쉬운 NoSQL 기반 데이터베이스인 MongoDB를 사용함으로써 NoSQL 데이터베이스의 사용법을 익힐 뿐 아니라 관계형 데이터베이스와 NoSQL 데이터베이스간의 차이점을 인식하는 것을 목적으로 한다.

## 뉴스 기사 전처리 과정
1. 형태소 분석 및 불용어 처리
2. 한 기사 내의 형태소 집합 구하기

## Apriori 알고리즘 구현
1. min sup을 만족시키는 frequent itemset 생성
2. strong 연관 규칙 생성

## 사용 환경
서버 : Host - xxxxxxx.sogang.ac.kr / Port - xx<br>
운영 체제 : Ubuntu 14.04.5 LTS<br>
데이터베이스 : Mongodb 3.0.14<br>
사용 언어 : PYTHON 2.7.6<br>
라이브러리 : pymongo, MeCab<br>
서버 계정 : xxxxxx<br>
서버 비번 : xxxxxx<br>
데이터베이스 계정 : xxxxxx<br>
데이터베이스 비번 : xxxxxx<br>