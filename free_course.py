from pymilvus import MilvusClient
import pandas as pd
from sentence_transformers import SentenceTransformer
import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger("pymilvus").setLevel(logging.WARNING)


class FreeCourse:

    def __init__(self):
        self.client = MilvusClient("free_courses.db")
        self.collection_name = "free_courses_collection"
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        logging.info("\tSetting up the vector database")
        self.setup_vector_db()

    def setup_vector_db(self):

        if self.client.has_collection(collection_name=self.collection_name):
            self.client.drop_collection(collection_name=self.collection_name)
        self.client.create_collection(
            collection_name="free_courses_collection",
            dimension=384,
        )

        # Load and Embed CSV Data
        csv_file = "free_course_list.csv"
        df = pd.read_csv(csv_file)

        # Prepare Data for Milvus
        data_list = []
        for i in range(len(df)):
            # print("Title:" + str(df['title'][i]) + "\n\n" + "Description:" + str(df['description'][i]) + "\n\n" + "Curriculum:" + str(df['Curriculum'][i]))
            data_list.append("Title:" + str(df['title'][i]) + "\n\n----\n\n" + "Description:" + str(df['description'][i]) + "\n\n----\n\n" + "Curriculum:" + str(df['curriculum'][i]) + "\n\n----\n\n" + "Course_URL:" + str(df['course_url'][i]))
        vectors = self.model.encode(data_list)


        data = [
            {"id": i, "vector": vectors[i], "text": data_list[i], "subject": "Free Courses"}
            for i in range(len(vectors))
        ]

        _ = self.client.insert(collection_name="free_courses_collection", data=data)
        logging.info("\tData inserted successfully into a Vector Database")

    def search(self, query, top_k=5):
        logging.info(f"\tSearching for {query}")
        query_vector = self.model.encode([query])
        results = self.client.search(
            collection_name=self.collection_name,
            data=query_vector,
            top_k=top_k,
            output_fields=["text", "subject"], 
        )

        related_courses = []
        for each_res in results[0]:

            final_result = each_res['entity']['text'].split('\n\n----\n\n')
            related_courses.append({
            "title": final_result[0].replace("Title:", ""),
            "description": final_result[1].replace("Description:", ""),
            "curicullum": final_result[2].replace("Curriculum:", ""),
            "url": final_result[3].replace("Course_URL:", "")
            })

        logging.info(f"\tFound {len(related_courses)} related courses")
        return related_courses
    



    

