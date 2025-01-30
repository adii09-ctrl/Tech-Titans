from urllib import request
import openai # type: ignore

openai.api_key = "your-openai-api-key"

def analyze_resume_with_gpt(resume_text):
    """Analyze a resume using GPT to extract key skills"""
    prompt = f"""
    Extract the most important skills, experience, and qualifications from the following resume:
    {resume_text}
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]

@app.route("/ai-screening", methods=["POST"]) # type: ignore
def ai_screening():
    """Analyze a resume using GPT"""
    data = request.json
    resume_text = data.get("resume_text")

    if not resume_text:
        return jsonify({"error": "No resume text provided"}), 400 # type: ignore

    ai_analysis = analyze_resume_with_gpt(resume_text)
    return jsonify({"analysis": ai_analysis}) # type: ignore
