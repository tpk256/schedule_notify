(async function() {
  // Получаем JWT из localStorage
  const token = localStorage.getItem('jwt');

  // URL для редиректа на страницу логина
  const loginUrl = "/login/";
  // URL для валидации токена
  const validateUrl = "/token/validate/";

  // Если токена нет — сразу редиректим
  if (!token) {
    window.location.href = loginUrl;
    return;
  }

  try {
    // Отправляем запрос на валидацию токена
    const res = await fetch(validateUrl, {
      method: "POST",
      headers: {
        'Authorization': 'Bearer ' + token
      }
    });

    // При неуспешной валидации — очищаем и редирект
    if (!res.ok) {
      localStorage.removeItem('jwt');
      const next = encodeURIComponent(window.location.pathname + window.location.search);
      window.location.href = `${loginUrl}?next=${next}`;
      return;
    }

    // Токен валиден — дальше загружается контент страницы
  } catch (err) {
    console.error('Validation error:', err);
    localStorage.removeItem('jwt');
    window.location.href = loginUrl;
  }
})();