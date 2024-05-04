import streamlit as st
import db
import my_openai


def select_interview() -> int:
    if 'selected_interview' not in st.session_state or not st.session_state['selected_interview']:
        return 0
    return st.session_state['selected_interview']


def display_data_by_interview(interview_id: int):
    st.header('Interview Detail')
    st.write(f"面试ID: {interview_id}")
    sentences = db.get_sentence_by_interview(interview_id)
    for sentence in sentences:
        st.write(f"句子ID: {sentence.id} | 角色: {sentence.role} | 时长: {sentence.duration} | 开始时间: {sentence.create_time.strftime('%Y-%m-%d %H:%M:%S')}")
        st.write(f"原文: {sentence.origin_sentence}")
        st.write(f"译文: {sentence.ai_sentence}")
        st.write("")

def display_interview_dimension(interview_id: int):
    if st.sidebar.button("返回", key='goback_project'):
        st.session_state['selected_interview'] = 0
        st.experimental_rerun()
    st.sidebar.title("Interview Selection")
    selected_project_id = st.session_state.get('selected_project', 0)  # 使用get方法，默认为0
    interviews = db.get_all_interview(selected_project_id)
    interview_options = {f"ID {interview.id} - {interview.create_time.strftime('%Y-%m-%d')}": interview.id for
                         interview in interviews}
    default_idx = 0
    for idx, (key, value) in enumerate(interview_options.items()):
        if value == interview_id:
            default_idx = idx
            break
    selected_interview = st.sidebar.radio("Choose a project:", list(interview_options.keys()), index=default_idx,
                                          format_func=lambda x: x)

    if interview_options[selected_interview] != interview_id:
        st.session_state['selected_interview'] = interview_options[selected_interview]
        st.experimental_rerun()
    display_data_by_interview(interview_options[selected_interview])


def display_data_by_project(project_id: int):
    interviews = db.get_project_data(project_id)
    labels = {}
    # 聚合标签数据
    for interview in interviews:
        for sentence in interview.sentences:
            if sentence.label not in labels:
                labels[sentence.label] = []
            labels[sentence.label].append(sentence)

    # 展示
    st.subheader('标签聚合信息')
    for label, sentences in labels.items():
        with st.expander(f"Label: {label}"):
            st.subheader(f"Label: {label}")
            st.subheader("标签总结：")
            # 实时调用openai处理
            st.write(my_openai.get_tag_summary(sentences))
            st.subheader("相关对话：")
            for sentence in sentences:
                sentence_display = f"{sentence.role}: {sentence.ai_sentence} -- {sentence.create_time.strftime('%Y-%m-%d %H:%M:%S')}"
                st.text(sentence_display)

    st.subheader("面试列表")
    for interview in interviews:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"面试ID: {interview.id} | 时长: {interview.duration} | 开始时间: {interview.create_time.strftime('%Y-%m-%d %H:%M:%S')}")
        with col2:
            if st.button("面试详情", key=interview.id):  # 为每个面试添加详情按钮，注意key的设置避免重复
                st.session_state['selected_interview'] = interview.id
                st.session_state['selected_project'] = project_id
                st.experimental_rerun()


def display_project_dimension():
    st.sidebar.title("Project Selection")
    projects = db.get_all_projects()
    project_options = {f"ID {proj['project_id']} - {proj['create_time'].strftime('%Y-%m-%d')}": proj['project_id'] for
                       proj in projects}
    selected_project_id = st.session_state.get('selected_project', 0)  # 使用get方法，默认为0
    default_idx = 0

    if selected_project_id != 0:
        for idx, (key, value) in enumerate(project_options.items()):
            if value == selected_project_id:  # 直接比较值
                default_idx = idx
                break

    selected_project = st.sidebar.radio("Choose a project:", list(project_options.keys()), index=default_idx,
                                        format_func=lambda x: x)
    if project_options[selected_project] != selected_project_id:
        st.session_state['selected_project'] = project_options[selected_project]
        st.experimental_rerun()
    display_data_by_project(project_options[selected_project])


if __name__ == "__main__":
    interview_id = select_interview()
    if interview_id == 0:
        display_project_dimension()
    else:
        display_interview_dimension(interview_id)
