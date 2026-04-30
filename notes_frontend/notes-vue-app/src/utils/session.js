import axios from 'axios';

const USER_ID_KEY = 'notes_user_id';

export function getUserId() {
    return localStorage.getItem(USER_ID_KEY);
}

export async function initUserId() {
    // Проверяем, есть ли уже сохраненный ID
    let userId = localStorage.getItem(USER_ID_KEY);
    
    if (userId && userId !== 'unknown') {
        console.log('✅ Using existing User ID:', userId);
        return userId;
    }

    // Если нет — запрашиваем новый с сервера
    try {
        const response = await axios.post('/api/create-session/');
        userId = response.data.user_id;
        localStorage.setItem(USER_ID_KEY, userId);
        console.log('✅ New User ID created:', userId);
        return userId;
    } catch (error) {
        console.warn('⚠️ Failed to get server user_id, generating local:', error);
        // Запасной вариант — генерируем локально
        userId = 'user_' + Math.random().toString(36).substring(2, 15);
        localStorage.setItem(USER_ID_KEY, userId);
        return userId;
    }
}

export function setupAxiosInterceptors() {
    axios.interceptors.request.use(config => {
        const userId = localStorage.getItem(USER_ID_KEY);
        if (userId && userId !== 'unknown') {
            config.headers['X-User-ID'] = userId;
        }
        return config;
    });
}