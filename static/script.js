const signUpButton = document.getElementById('signUp');
const signInButton = document.getElementById('signIn');
const container = document.getElementById('container');

// 회원가입 버튼 클릭 시
signUpButton.addEventListener('click', () => {
    // 'right-panel-active' 클래스를 추가하여 Sign Up 폼을 표시합니다.
    container.classList.add("right-panel-active");
});

// 로그인 버튼 클릭 시
signInButton.addEventListener('click', () => {
    // 'right-panel-active' 클래스를 제거하여 Sign In 폼을 표시합니다.
    container.classList.remove("right-panel-active");
});