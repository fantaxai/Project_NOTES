import axios from 'axios';

const USER_ID_KEY = 'notes_user_id';

// Получаем или создаем user_id
export function getUserId() {
    let userId = localStorage.getItem(USER_ID_KEY);
    if (!userId) {
        // Если нет - создаем временный
        userId = generateTempId();
        localStorage.setItem(USER_ID_KEY, userId);
        // Асинхронно получаем постоянный ID
        initUserId().catch(console.warn);
    }
    return userId;
}

function generateTempId() {
    return 'temp_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// Получаем постоянный ID с сервера
export async function initUserId() {
    try {
        const response = await axios.post('/api/create-session/');
        const userId = response.data.user_id;
        localStorage.setItem(USER_ID_KEY, userId);
        console.log('✅ User ID initialized:', userId);
        return userId;
    } catch (error) {
        console.warn('⚠️ Failed to get server user_id, using local:', error);
        return getUserId();
    }
}

// Настройка axios для отправки user_id во всех запросах
export function setupAxiosInterceptors() {
    axios.interceptors.request.use(config => {
        const userId = localStorage.getItem(USER_ID_KEY);
        if (userId && !userId.startsWith('temp_')) {
            config.headers['X-User-ID'] = userId;
        }
        return config;
    });

    // Перехватчик ошибок для отладки
    axios.interceptors.response.use(
        response => response,
        error => {
            if (error.response?.status === 404) {
                console.warn('API endpoint not found:', error.config?.url);
            }
            return Promise.reject(error);
        }
    );
}