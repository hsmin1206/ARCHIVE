import os
import csv
import sqlite3
import pandas as pd
import glob

def csv_to_sqlite(data_folder, db_name):
    """
    데이터 폴더의 모든 CSV 파일을 SQLite 데이터베이스로 변환합니다.
    
    Args:
        data_folder (str): CSV 파일이 저장된 폴더 경로
        db_name (str): 생성할 SQLite 데이터베이스 파일 이름
    """
    # SQLite 데이터베이스 연결
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # 데이터 폴더의 모든 CSV 파일 경로 가져오기
    csv_files = glob.glob(os.path.join(data_folder, "*.csv"))
    
    if not csv_files:
        print(f"{data_folder} 폴더에 CSV 파일이 없습니다.")
        return
    
    print(f"총 {len(csv_files)}개의 CSV 파일을 발견했습니다.")
    
    # 각 CSV 파일을 SQLite 테이블로 변환
    for csv_file in csv_files:
        # 파일 이름에서 테이블 이름 추출 (확장자 제외)
        table_name = os.path.splitext(os.path.basename(csv_file))[0]
        
        # pandas를 사용하여 CSV 파일 읽기
        try:
            df = pd.read_csv(csv_file, encoding='utf-8')
        except UnicodeDecodeError:
            # UTF-8로 읽기 실패 시 다른 인코딩 시도
            try:
                df = pd.read_csv(csv_file, encoding='cp949')  # 한글 Windows 인코딩
            except Exception as e:
                print(f"파일 읽기 실패: {csv_file}, 오류: {e}")
                continue
        
        # DataFrame을 SQLite 테이블로 저장
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        print(f"'{table_name}' 테이블 생성 완료 ({len(df)} 행)")
    
    # 데이터베이스의 모든 테이블 스키마 정보 출력 및 텍스트 파일로 저장
    schema_info = []
    
    # 모든 테이블 목록 가져오기
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        
        # 테이블 정보 가져오기
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        # 스키마 정보 저장
        schema_info.append(f"\n테이블: {table_name}")
        schema_info.append("=" * 50)
        
        # 열 정보 출력
        for col in columns:
            col_id, col_name, col_type, not_null, default_val, pk = col
            schema_info.append(f"  {col_name} ({col_type})")
            if pk:
                schema_info.append("    - 기본 키(Primary Key)")
            if not_null:
                schema_info.append("    - NOT NULL")
            if default_val is not None:
                schema_info.append(f"    - 기본값: {default_val}")
        
        # 샘플 데이터 개수
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        row_count = cursor.fetchone()[0]
        schema_info.append(f"  총 {row_count}개의 행이 있습니다.")
    
    # 스키마 정보 출력
    schema_text = "\n".join(schema_info)
    print("\n데이터베이스 스키마 정보:")
    print(schema_text)
    
    # 스키마 정보를 텍스트 파일로 저장
    schema_file = "db_schema.txt"
    with open(schema_file, "w", encoding="utf-8") as f:
        f.write(schema_text)
    
    print(f"\n스키마 정보가 '{schema_file}' 파일에 저장되었습니다.")
    
    # 연결 종료
    conn.close()
    print(f"\n모든 작업이 완료되었습니다. 데이터베이스 파일: {db_name}")

if __name__ == "__main__":
    data_folder = "data"  # CSV 파일이 있는 폴더 경로
    db_name = "database.db"  # 생성할 SQLite 데이터베이스 파일 이름
    
    # CSV 파일을 SQLite로 변환
    csv_to_sqlite(data_folder, db_name)
    
    # 5/21은 여기까지!!