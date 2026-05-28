import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [categories, setCategories] = useState([]);
  const [formData, setFormData] = useState({
    name: '', weight: '', price: '', category_id: '', image: null
  });

  useEffect(() => {
    // Загружаем категории с поддержкой куки
    axios.get('http://127.0.0.1:5000/api/categories', { withCredentials: true })
      .then(res => setCategories(res.data))
      .catch(err => console.error("Ошибка загрузки категорий:", err));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if(!formData.category_id) {
        alert("Выберите категорию!");
        return;
    }

    const data = new FormData();
    data.append('name', formData.name);
    data.append('weight', formData.weight);
    data.append('price', formData.price);
    data.append('category_id', formData.category_id);
    if (formData.image) {
        data.append('image', formData.image);
    }

    try {
        // Добавляем { withCredentials: true } для передачи сессии
        await axios.post('http://127.0.0.1:5000/api/products', data, { withCredentials: true });
        alert("Товар добавлен!");
        window.location.reload(); 
    } catch (error) {
        console.error("Ошибка при отправке:", error);
        // Если пришла ошибка 401, значит сессия истекла
        if (error.response && error.response.status === 401) {
            alert("Ваша сессия истекла. Пожалуйста, войдите в систему снова.");
            window.location.href = "http://127.0.0.1:5000/login";
        } else {
            alert("Ошибка сети!");
        }
    }
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Добавление товара</h2>
      <form onSubmit={handleSubmit} style={styles.form}>
        <input type="text" placeholder="Название" onChange={e => setFormData({...formData, name: e.target.value})} style={styles.input} />
        <input type="text" placeholder="Вес (например, 200 г)" onChange={e => setFormData({...formData, weight: e.target.value})} style={styles.input} />
        <input type="number" placeholder="Цена" onChange={e => setFormData({...formData, price: e.target.value})} style={styles.input} />
        
        <select onChange={e => setFormData({...formData, category_id: e.target.value})} style={styles.input}>
          <option value="">Выберите категорию</option>
          {categories.map(cat => (
            <option key={cat.id} value={cat.id}>{cat.name}</option>
          ))}
        </select>

        <input type="file" onChange={e => setFormData({...formData, image: e.target.files[0]})} style={styles.fileInput} />
        
        <button type="submit" style={styles.button}>Сохранить</button>
      </form>
    </div>
  );
}

const styles = {
  container: { backgroundColor: '#FDFBF7', minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '50px' },
  title: { color: '#5D5D5D', marginBottom: '30px', fontWeight: '300' },
  form: { backgroundColor: '#FFFFFF', padding: '40px', borderRadius: '15px', boxShadow: '0 4px 15px rgba(0,0,0,0.05)', display: 'flex', flexDirection: 'column', width: '400px' },
  input: { marginBottom: '15px', padding: '12px', border: '1px solid #EFEFEF', borderRadius: '8px', backgroundColor: '#FAFAFA', outline: 'none' },
  fileInput: { marginBottom: '20px' },
  button: { backgroundColor: '#D4E1D1', color: '#5D5D5D', border: 'none', padding: '15px', borderRadius: '8px', cursor: 'pointer', fontSize: '16px' }
};

export default App;





