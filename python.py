import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer     # type: ignore
from sklearn.metrics.pairwise import cosine_similarity   # type: ignore

class ResumeScanner:
    def __init__(self, job_descriptions):
        """Initializes the ResumeScanner with a list of job descriptions."""
        self.job_descriptions = job_descriptions
        self.resumes = []

    def add_resume(self, resume_text):
        """Adds a resume to the scanner."""
        self.resumes.append(resume_text)

    def preprocess_text(self, text):
        """Cleans and normalizes the input text."""
        text = text.lower()
        text = re.sub(r'\W+', ' ', text)
        return text

    def rank_candidates(self):
        """Ranks the added resumes based on their similarity to the job descriptions."""
        if not self.resumes:
            return []

        # Preprocess job descriptions and resumes
        processed_descriptions = [self.preprocess_text(desc) for desc in self.job_descriptions]
        processed_resumes = [self.preprocess_text(resume) for resume in self.resumes]

        # Vectorize the job descriptions and resumes
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform(processed_descriptions + processed_resumes)

        # Calculate cosine similarity for each job description
        rankings = []
        for i in range(len(processed_descriptions)):
            cosine_similarities = cosine_similarity(vectors[i:i+1], vectors[len(processed_descriptions):]).flatten()
            ranked_candidates = sorted(enumerate(cosine_similarities), key=lambda x: x[1], reverse=True)
            rankings.append(ranked_candidates)

        return rankings

    def read_resumes_from_file(self, file_path):
        """Reads resumes from a specified text file."""
        with open(file_path, 'r') as file:
            resumes = file.readlines()
            for resume in resumes:
                self.add_resume(resume.strip())

    def write_rankings_to_file(self, rankings, output_file):
        """Writes the ranking results to a specified output file."""
        with open(output_file, 'w') as file:
            for i, ranked in enumerate(rankings):
                file.write(f"Job Description {i+1} Rankings:\n")
                for index, score in ranked:
                    file.write(f"Candidate {index + 1}: Score {score}\n")
                file.write("\n")

# Example usage
if __name__ == "__main__":
    job_descs = [
        "Looking for a software engineer with experience in Python and machine learning.",
        "Seeking a data analyst with strong SQL skills."
    ]
    scanner = ResumeScanner(job_descs)

    # Read resumes from a file
    scanner.read_resumes_from_file('resumes.txt')  # Ensure this file exists with resumes

    # Rank candidates
    rankings = scanner.rank_candidates()
    scanner.write_rankings_to_file(rankings, 'rankings.txt')
    print("Rankings have been written to rankings.txt")
