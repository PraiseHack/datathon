
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import pandas as pd
import psycopg2
from psycopg2 import OperationalError
from dotenv import load_dotenv
import os

default_args = {
    'owner': 'stormdata',
    'start_date': datetime(2024, 10, 7),
}

# Load environment variables
load_dotenv()

def students_data():
    df = pd.read_csv("/opt/airflow/data/student_performance_data.csv")
    print(df.columns)
    return df

def transform_data(**kwargs):
    ti = kwargs['ti']
    df = ti.xcom_pull(task_ids='extract_students_data')  # Get DataFrame from extract task

    students_df = df[['student_id', 'gender', 'age']]
    academic_performance_df = df[['student_id', 'jamb_score', 'mock_exam_score']]
    attendance_df = df[['student_id', 'attendance_rate']]
    health_records_df = df[['student_id']]
    teacher_feedback_df = df[['student_id', 'access_to_teachers']]
    family_background_df = df[['student_id', 'parent_education_level', 'parental_support']]

    students_df['gender'] = students_df['gender'].str.title()  
    students_df['age'] = students_df['age'].fillna(0).astype(int)  
    academic_performance_df.fillna(0, inplace=True)  
    academic_performance_df['jamb_score'] = academic_performance_df['jamb_score'].astype(float) 
    attendance_df['attendance_rate'] = attendance_df['attendance_rate'].astype(float)  

    # Average Exam Score per Student
    avg_exam_score = academic_performance_df.groupby('student_id')['jamb_score'].mean().reset_index()
    avg_exam_score.columns = ['student_id', 'avg_exam_score']
    students_df = students_df.merge(avg_exam_score, on='student_id', how='left')
    students_df['avg_exam_score'] = students_df['avg_exam_score'].fillna(0)

    # Return a dictionary of DataFrames to push to XCom
    data_dict = {
        'students': students_df,
        'academic_performance': academic_performance_df,
        'attendance': attendance_df,
        'health_records': health_records_df,
        'teacher_feedback': teacher_feedback_df,
        'family_background': family_background_df
    }

    ti.xcom_push(key='data_dict', value=data_dict)  # Push the transformed data

def get_pg_creds():
    return {
        "user": os.environ.get("POSTGRES_USER"),
        "password": os.environ.get("POSTGRES_PASSWORD"),
        "host": os.environ.get("POSTGRES_HOST", "localhost"),
        "port": os.environ.get("POSTGRES_PORT", 5435),
        "dbname": os.environ.get("POSTGRES_DBNAME"),
    }

# Start PostgreSQL connection
def start_postgres_connection():
    creds = get_pg_creds()
    try:
        connection = psycopg2.connect(
            user=creds["user"],
            password=creds["password"],
            host=creds["host"],
            port=creds["port"],
            dbname=creds["dbname"],
        )
        print("Connection to PostgreSQL DB successful")
        return connection
    except OperationalError as e:
        print(f"The error '{e}' occurred")
        return None

# Load data into PostgreSQL
def load_data(**kwargs):
    ti = kwargs['ti']
    data_dict = ti.xcom_pull(task_ids='transform_data', key='data_dict')  # Pull the transformed data

    conn = start_postgres_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()

            for table_name, df in data_dict.items():
                for index, row in df.iterrows():
                    insert_query = f"""
                    INSERT INTO {table_name} ({', '.join(df.columns)})
                    VALUES ({', '.join(['%s'] * len(row))})
                    """
                    cursor.execute(insert_query, tuple(row))

            conn.commit()  # Commit the transaction
            print("Data loaded successfully")
        except Exception as e:
            print(f"An error occurred while loading data: {e}")
        finally:
            cursor.close()
            conn.close()

with DAG('student_data_pipeline', 
         default_args=default_args, 
         schedule_interval='@daily') as dag:

    
    task_extract = PythonOperator(
        task_id='extract_students_data',
        python_callable=students_data,
    )

    task_transform = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data,
        provide_context=True,  
    )

    task_load = PythonOperator(
        task_id='load_data',
        python_callable=load_data,
        provide_context=True,  
    )

    task_extract >> task_transform >> task_load
