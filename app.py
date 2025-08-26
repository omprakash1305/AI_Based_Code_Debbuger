import streamlit as st
from streamlit_ace import st_ace
import subprocess
import os
import time
from groq import Groq
import config
import platform

TEMP_DIR = "temp_files"
os.makedirs(TEMP_DIR, exist_ok=True)

st.set_page_config(page_title="Matics Editor", page_icon="📝", layout="wide")


def initialize_session_state():
    if 'execution_history' not in st.session_state:
        st.session_state['execution_history'] = {}
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    if 'output' not in st.session_state:  
        st.session_state['output'] = ""
    if 'debug_suggestions' not in st.session_state: 
        st.session_state['debug_suggestions'] = ""
    if 'process' not in st.session_state: 
        st.session_state['process'] = None



client = Groq(api_key=config.GROQ_API_KEY)



def configure_sidebar():
    st.header("MATICS EDITOR 📝")


    MODEL_NAME_MAPPING = {
        "deepseek-r1-distill-llama-70b": "DeepSeek R1 (Not Recommended for Coding)",
        "gemma2-9b-it": "Gemma 2 9B",
        "llama-3.1-8b-instant": "Llama 3.1-8B",
        "llama-3.2-90b-vision-preview": "Llama 3.2-90B",
        "llama-3.3-70b-versatile": "Llama 3.3-70B",
        "llama3-70b-8192": "Llama3 70B",
        "llama3-8b-8192": "Llama3 8B",
        "mixtral-8x7b-32768": "Mixtral 8x7B",
        "qwen-2.5-coder-32b": "Qwen 2.5 Coder 32B"
    }


    model_options = list(MODEL_NAME_MAPPING.keys())


    display_models = [MODEL_NAME_MAPPING.get(model, model) for model in model_options]


    default_model_name = "Llama 3.1-8B"
    default_index = display_models.index(default_model_name) if default_model_name in display_models else 0


    selected_model_display = st.selectbox("Choose AI Model", display_models, index=default_index)


    selected_model = next((key for key, value in MODEL_NAME_MAPPING.items() if value == selected_model_display), selected_model_display)

    with st.sidebar:
        st.header("Web Development")
        web_modules = st.checkbox("Enable Web Framework")

        web_framework = None
        django_project_name = ""

        if web_modules:
            web_framework = st.radio("Select Web Framework:", ["Django", "Flask", "Streamlit"])
            if web_framework == "Django":
                django_project_name = st.text_input("Django Project Name:", value="myproject")
            if st.button("Install Required Modules"):
                install_modules(web_framework)

        st.header("Editor Settings")
        theme = st.selectbox("Editor Theme", ["monokai", "github", "solarized_dark", "solarized_light", "dracula"], index=0)
        font_size = st.slider("Font Size", 12, 24, 14)
        show_gutter = st.checkbox("Show Line Numbers", value=True)

        language = st.selectbox("Language", ["Python", "Java", "C", "C++"], index=0)
        
        return theme, font_size, show_gutter, language, web_modules, web_framework, django_project_name, selected_model



def install_modules(web_framework):
    modules = {"Flask": "flask", "Django": "django", "Streamlit": "streamlit"}
    
    if web_framework in modules:
        module_name = modules[web_framework]
        st.info(f"Installing {module_name}...")
        subprocess.run(["pip", "install", module_name])
        st.success(f"{module_name} installed successfully!")


def get_default_code(language):
    return {
        "Python": 'print("Hello, World!")',
        "Java": 'public class Main { public static void main(String[] args) { System.out.println("Hello, World!"); } }',
        "C": '#include <stdio.h>\nint main() { printf("Hello, World!\\n"); return 0; }',
        "C++": '#include <iostream>\nusing namespace std;\nint main() { cout << "Hello, World!" << endl; return 0; }'
    }[language]


def code_editor(theme, font_size, show_gutter, language, default_code):
    return st_ace(
        language=language.lower() if language in ["Python", "Java"] else "c_cpp",
        theme=theme,
        font_size=font_size,
        show_gutter=show_gutter,
        auto_update=True,
        key="editor",
        value=default_code
    )


def run_code(language, code, web_modules=False, web_framework=None, django_project_name="myproject"):
    temp_files = {
    "Python": os.path.join(TEMP_DIR, "temp_script.py"),
    "Java": os.path.join(TEMP_DIR, "Main.java"),
    "C": os.path.join(TEMP_DIR, "temp_C_program.c"),
    "C++": os.path.join(TEMP_DIR, "temp_C++_program.cpp")
    }

    
    temp_file = temp_files.get(language, "temp_script.py")


    if st.session_state.get('process'):
        stop_process()


    with open(temp_file, "w") as f:
        f.write(code)
    

    if web_modules:
        if web_framework == "Django":
            try:
                django_project_path = os.path.join(TEMP_DIR, django_project_name)
                if not os.path.exists(django_project_path):
                    os.system(f"django-admin startproject {django_project_name} {django_project_path}")
                    st.success(f"Django project '{django_project_name}' created!")
                    os.chdir(django_project_path)

                
                st.session_state['process'] = subprocess.Popen(
                    ["python", "manage.py", "runserver", "8002"],  
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                st.success("Django server running! [Click here to open](http://127.0.0.1:8002)")
            except Exception as e:
                st.error(f"Error running Django: {e}")
            finally:
                os.chdir("..") 

        elif web_framework == "Flask":
            try:
                st.session_state['process'] = subprocess.Popen(
                    ["python", temp_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                st.success("Flask server running! [Click here to open](http://127.0.0.1:5000)")
            except Exception as e:
                st.error(f"Error running Flask: {e}")

        elif web_framework == "Streamlit":
            try:
                st.session_state['process'] = subprocess.Popen(
                    ["streamlit", "run", temp_file, "--server.port=8502"],  
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                st.success("Streamlit app running! [Click here to open](http://localhost:8502)")
            except Exception as e:
                st.error(f"Error running Streamlit: {e}")
    

    else:
        try:
            user_input = st.text_area("Enter Input", "", height=100)
            
            if language == "Python":
                result = subprocess.run(["python", temp_file], capture_output=True, text=True, input=user_input)

            elif language == "Java":
                java_dir = "temp_files"
                

                temp_file = os.path.basename(temp_file)  
                temp_file_path = os.path.join(java_dir, temp_file) 
                

                compile_result = subprocess.run(["javac", temp_file_path], capture_output=True, text=True)
                
                if compile_result.returncode == 0:

                    class_name = os.path.splitext(temp_file)[0]


                    result = subprocess.run(["java", "-cp", java_dir, class_name], capture_output=True, text=True, input=user_input)
                else:
                    result = compile_result


            elif language == "C":
                c_dir = "temp_files"


                temp_file = os.path.basename(temp_file)  
                temp_file_path = os.path.join(c_dir, temp_file)  
                output_exe = os.path.join(c_dir, "temp_C_program")

                if os.path.exists(output_exe):
                    os.remove(output_exe)

                compile_result = subprocess.run(["gcc", temp_file_path, "-o", output_exe], capture_output=True, text=True)

                if compile_result.returncode == 0:

                    exec_cmd = output_exe if platform.system() == "Windows" else f"./{output_exe}"
                    result = subprocess.run(exec_cmd, capture_output=True, text=True, input=user_input)
                else:
                    result = compile_result


            elif language == "C++":
                cpp_dir = "temp_files"

                temp_file = os.path.basename(temp_file)  
                temp_file_path = os.path.join(cpp_dir, temp_file)  
                output_exe = os.path.join(cpp_dir, "temp_cpp_program") 

                if os.path.exists(output_exe):
                    os.remove(output_exe)

                compile_result = subprocess.run(["g++", temp_file_path, "-o", output_exe], capture_output=True, text=True)

                if compile_result.returncode == 0:

                    exec_cmd = output_exe if platform.system() == "Windows" else f"./{output_exe}"
                    result = subprocess.run(exec_cmd, capture_output=True, text=True, input=user_input)
                else:
                    result = compile_result

            
            else:
                st.error("Unsupported language selected.")
                return
            

            timestamp = time.time()
            st.session_state['execution_history'][timestamp] = (code, result.stdout if result.stdout else result.stderr)
            st.session_state['output'] = result.stdout if result.stdout else result.stderr
        
        except Exception as e:
            st.error(f"Execution failed: {e}")




def analyze_code(code, output, language, model):
    is_error = "Traceback" in output or "Error" in output

    system_prompt = f"You are a smart assistant for debugging and enhancing {language} code. Respond concisely with structured output."
    user_prompt = f"Here is the {language} script:\n\n{code}\n\nAnd here is the execution output:\n\n{output}\n\n"
    title_prompt = f"Generate only a 5-8 word title summarizing this {language} code issue or functionality. Do not provide any explanation."


    try:
        response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
            {"role": "user", "content": title_prompt}
        ],
        model=model, 
        temperature=0.3,
        max_tokens=1024
    )


        if response and response.choices:
            generated_title = response.choices[0].message.content.strip()

            suggestions_response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model="llama3-8b-8192",
                temperature=0.5,
                max_tokens=1024
            )

            suggestions = suggestions_response.choices[0].message.content.strip() if suggestions_response.choices else "No debugging suggestions available."

            st.session_state['debug_suggestions'] = suggestions  

            st.session_state['chat_history'].append({
                "title": generated_title,  
                "code": code,
                "output": output,
                "suggestions": suggestions
            })

        else:
            st.session_state['debug_suggestions'] = "No response from the AI."

    except Exception as e:
        st.session_state['debug_suggestions'] = f"Error fetching suggestions: {e}"



def stop_process():
    if st.session_state['process']:
        st.session_state['process'].terminate()
        st.session_state['process'] = None
        st.warning("Process stopped.")
        os.chdir("..")  


initialize_session_state()
theme, font_size, show_gutter, language, web_modules, web_framework, django_project_name, selected_model = configure_sidebar()
default_code = get_default_code(language)
code = code_editor(theme, font_size, show_gutter, language, default_code)

if st.button("Run Code"):
    run_code(language, code, web_modules, web_framework, django_project_name)
    analyze_code(code, st.session_state['output'], language, selected_model) 

if st.button("Stop Running Process"):
    stop_process()

st.subheader("Console Output")
st.text_area("Console Output", st.session_state['output'], height=200, disabled=True)


if "debug_suggestions" in st.session_state:
    st.subheader("Code Enhancement & Debugging Suggestions")
    st.text_area("AI Feedback", st.session_state['debug_suggestions'], height=200, disabled=True)


st.subheader("Chat History")
for i, entry in enumerate(st.session_state['chat_history']): 
    title = f"Chat History {i+1} - {entry.get('title', 'Code and Suggestions')}"
    with st.expander(f"{title}"):
        st.code(entry['code'], language=language.lower() if language in ["Python", "Java"] else "c_cpp")
        st.text_area(f"Execution Output {i+1}", 
                     entry['output'], height=100, disabled=True, key=f"exec_output_{i+1}")
        st.text_area(f"AI Feedback {i+1}", 
                     entry['suggestions'], height=200, disabled=True, key=f"AI_feedback_{i+1}")
        
st.markdown(
    """
    <div style="position: fixed; bottom: 10px; right: 10px; 
                color: #bbb; font-size: 14px;">
        Developed by <a href="https://github.com/darkness0308" 
        style="color: #bbb; text-decoration: none;">darkness_0308</a>
    </div>
    """,
    unsafe_allow_html=True
)

