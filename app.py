from flask import Flask, render_template, request, jsonify
from groq import Groq
app = Flask(__name__)

# Custom Jinja2 filter to split strings
def split_filter(value, delimiter='\n'):
    return value.split(delimiter) if value else []

# Register the custom filter
app.jinja_env.filters['split'] = split_filter

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/form')
def form():
    template = request.args.get('template', 'template1')  # Get template from URL
    return render_template('index.html', selected_template=template)

@app.route('/preview', methods=['POST'])
def preview():
    data = request.form.to_dict()
    template = data.get('template', 'template1')
    return render_template('preview.html', template=template, data=data)

@app.route('/add_custom_field', methods=['POST'])
def add_custom_field():
    field_name = request.form.get('custom_field')
    return jsonify({'status': 'success', 'field_name': field_name})

@app.route('/check_resume', methods=['POST'])
def check_resume():
    data = request.form.to_dict()

    score = 0
    max_score = 100  # Changed to 100-point scale
    feedback = []
    sections = {}

    # 1. Contact Information (5 points)
    contact_fields = ['name', 'email', 'phone', 'linkedin', 'portfolio']
    missing_contact = [field for field in contact_fields if not data.get(field)]
    contact_score = 5 - len(missing_contact)
    score += contact_score
    if missing_contact:
        feedback.append(f"Missing contact information: {', '.join(missing_contact)}")
    sections['contact_info'] = {
        'score': contact_score,
        'max': 5,
        'feedback': f"Contact completeness: {contact_score}/5"
    }

    # 2. Professional Summary (10 points)
    summary = data.get('summary', '')
    summary_score = 0
    
    # Length check (30-50 words ideal)
    word_count = len(summary.split())
    if word_count >= 30:
        summary_score += 4
    elif word_count >= 15:
        summary_score += 2
        
    # Keyword check
    summary_keywords = ['experienced', 'skilled', 'professional', 'passionate', 'specialized']
    found_keywords = [word for word in summary_keywords if word in summary.lower()]
    if len(found_keywords) >= 2:
        summary_score += 3
        
    # Achievement mention
    if any(word in summary.lower() for word in ['achieved', 'result', 'impact', 'improved']):
        summary_score += 3
        
    score += summary_score
    sections['summary'] = {
        'score': summary_score,
        'max': 10,
        'feedback': f"Summary strength: {summary_score}/10 - {'Good' if summary_score >=7 else 'Needs improvement'}"
    }

    # 3. Work Experience (30 points)
    experience = data.get('experience', '')
    experience_score = 0
    
    # Length check
    exp_word_count = len(experience.split())
    if exp_word_count >= 100:
        experience_score += 10
    elif exp_word_count >= 50:
        experience_score += 5
        
    # Achievement metrics
    achievement_words = ['increased', 'reduced', 'saved', 'improved', 'achieved', 'led']
    achievement_count = sum(1 for word in achievement_words if word in experience.lower())
    experience_score += min(achievement_count, 5)  # Max 5 points
    
    # Action verbs
    action_verbs = ['developed', 'implemented', 'designed', 'managed', 'created', 'optimized']
    verb_count = sum(1 for word in action_verbs if word in experience.lower())
    experience_score += min(verb_count, 5)  # Max 5 points
    
    # Quantifiable results
    quantifiable = any(char in experience for char in ['%', '$', '+']) or \
                  any(word in experience.lower() for word in ['x%', 'times', 'to $'])
    if quantifiable:
        experience_score += 5
        
    # Job progression
    if 'senior' in experience.lower() or 'lead' in experience.lower() or 'manager' in experience.lower():
        experience_score += 5
        
    score += experience_score
    sections['experience'] = {
        'score': experience_score,
        'max': 30,
        'feedback': f"Experience quality: {experience_score}/30 - {'Strong' if experience_score >=20 else 'Could be stronger'}"
    }

    # 4. Skills Section (15 points)
    skills = data.get('skills', '').lower()
    skills_score = 0
    
    # Technical skills
    tech_skills = ['python', 'java', 'sql', 'javascript', 'c++', 'html', 'css', 
                  'react', 'node', 'aws', 'docker', 'git', 'machine learning']
    tech_count = sum(1 for skill in tech_skills if skill in skills)
    skills_score += min(tech_count, 5)  # Max 5 points
    
    # Soft skills
    soft_skills = ['communication', 'teamwork', 'leadership', 'problem solving', 
                  'time management', 'adaptability', 'collaboration']
    soft_count = sum(1 for skill in soft_skills if skill in skills)
    skills_score += min(soft_count, 3)  # Max 3 points
    
    # Tools/platforms
    tools = ['jira', 'jenkins', 'kubernetes', 'tableau', 'power bi', 'photoshop']
    tools_count = sum(1 for tool in tools if tool in skills)
    skills_score += min(tools_count, 3)  # Max 3 points
    
    # Organization
    if '\n' in skills or ',' in skills or '•' in skills:
        skills_score += 2
    elif ' ' in skills:
        skills_score += 1
        
    # Relevance (check for job-specific keywords)
    job_keywords = {
        'developer': ['coding', 'debugging', 'framework', 'api'],
        'designer': ['ui/ux', 'figma', 'wireframe', 'prototype'],
        'analyst': ['data', 'excel', 'visualization', 'statistics']
    }
    # Add more as needed
    
    score += skills_score
    sections['skills'] = {
        'score': skills_score,
        'max': 15,
        'feedback': f"Skills relevance: {skills_score}/15 - {'Comprehensive' if skills_score >=10 else 'Could expand'}"
    }

    # 5. Education (10 points)
    education = data.get('education', '')
    education_score = 0
    
    # Degree mention
    degree_words = ['bachelor', 'master', 'phd', 'diploma', 'degree']
    if any(word in education.lower() for word in degree_words):
        education_score += 4
        
    # Institution mention
    if 'university' in education.lower() or 'institute' in education.lower() or 'college' in education.lower():
        education_score += 3
        
    # GPA/achievements
    if 'gpa' in education.lower() or 'grade' in education.lower() or 'honors' in education.lower():
        education_score += 3
        
    score += education_score
    sections['education'] = {
        'score': education_score,
        'max': 10,
        'feedback': f"Education details: {education_score}/10 - {'Complete' if education_score >=7 else 'Basic'}"
    }

    # 6. Projects (10 points)
    projects = data.get('projects', '')
    projects_score = 0
    
    if projects:
        # Project count
        project_count = projects.count('\n\n') + 1  # Rough count based on paragraphs
        projects_score += min(project_count, 3)  # Max 3 points
        
        # GitHub/links
        if 'github.com' in projects or 'http' in projects:
            projects_score += 2
            
        # Technologies mentioned
        tech_mentioned = sum(1 for tech in tech_skills if tech in projects.lower())
        projects_score += min(tech_mentioned, 3)  # Max 3 points
        
        # Results/impact
        if any(word in projects.lower() for word in ['result', 'impact', 'used by', 'featured']):
            projects_score += 2
            
    score += projects_score
    sections['projects'] = {
        'score': projects_score,
        'max': 10,
        'feedback': f"Project quality: {projects_score}/10 - {'Impressive' if projects_score >=7 else 'Could enhance'}"
    }

    # 7. Additional Sections (20 points)
    additional_score = 0
    
    # Certifications
    certifications = data.get('certifications', '')
    if certifications:
        cert_count = certifications.count('\n') + 1
        additional_score += min(cert_count * 2, 6)  # Max 6 points
        
    # Languages
    languages = data.get('languages', '')
    if languages:
        lang_count = languages.count(',') + 1
        additional_score += min(lang_count, 3)  # Max 3 points
        
    # Volunteer/Extracurricular
    if 'volunteer' in data or 'extracurricular' in data:
        additional_score += 3
        
    # Custom sections
    custom_sections = len([key for key in data.keys() if key not in [
        'name', 'email', 'summary', 'education', 'experience', 
        'skills', 'projects', 'certifications', 'languages'
    ]])
    additional_score += min(custom_sections, 4)  # Max 4 points
    
    # Formatting bonus
    if any(tag in str(data.values()) for tag in ['<b>', '<ul>', '<li>', '•']):
        additional_score += 4
        
    score += additional_score
    sections['additional'] = {
        'score': additional_score,
        'max': 20,
        'feedback': f"Additional sections: {additional_score}/20 - {'Excellent' if additional_score >=15 else 'Good' if additional_score >=10 else 'Basic'}"
    }

    # Final adjustments
    score = min(score, max_score)
    
    # Selection likelihood (more granular)
    if score >= 85:
        likelihood = "Very High"
        feedback.append("Your resume is very strong and competitive.")
    elif score >= 70:
        likelihood = "High"
        feedback.append("Your resume is good but could use some improvements.")
    elif score >= 50:
        likelihood = "Medium"
        feedback.append("Your resume needs several improvements to be competitive.")
    else:
        likelihood = "Low"
        feedback.append("Your resume needs significant improvements to be effective.")

    # ---------- GROQ AI ANALYSIS ---------- #
    client = Groq(api_key="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")

    resume_text = "\n".join([
        f"Name: {data.get('name', '')}",
        f"Email: {data.get('email', '')}",
        f"Summary: {data.get('summary', '')}",
        f"Education: {data.get('education', '')}",
        f"Experience: {data.get('experience', '')}",
        f"Skills: {data.get('skills', '')}",
        f"Projects: {data.get('projects', '')}",
        f"Certifications: {data.get('certifications', '')}",
        f"Languages: {data.get('languages', '')}"
    ])

    ai_feedback = ""
    try:
        chat_completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional resume reviewer. Give concise, practical suggestions for improvement without repeating obvious sections. Focus on tone, professionalism, and strength of content.Analyze the resume and give feedback using proper HTML formatting with <b>,<ul>, <li>, and line breaks. Avoid markdown style."
                },
                {
                    "role": "user",
                    "content": f"Please review this resume:\n\n{resume_text}"
                }
            ]
        )
        ai_feedback = chat_completion.choices[0].message.content
    except Exception as e:
        ai_feedback = f"AI feedback not available: {str(e)}"

    return jsonify({
        'score': score,
        'max_score': max_score,
        'selection_likelihood': likelihood,
        'feedback': feedback,
        'section_analysis': sections,
        'ai_feedback': ai_feedback
    })
if __name__ == '__main__':
    app.run(debug=True)