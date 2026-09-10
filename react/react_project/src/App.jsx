import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import ItemListPage from './pages/ItemListPage';
import ItemDetailPage from './pages/ItemDetailPage';
import ItemNewPage from './pages/ItemNewPage';
import ItemEditPage from './pages/ItemEditPage';
import LoginPage from './pages/LoginPage';
import NotFoundPage from './pages/NotFoundPage';
import ProtectedRoute from './components/ProtectedRoute';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="items" element={<ItemListPage />} />
          <Route path="items/:id" element={<ItemDetailPage />} />
          <Route path="login" element={<LoginPage />} />
          
          {/*  보호 라우트: 로그인한 사용자만 접근 가능 (중복 제거 후 단일 선언) */}
          <Route path="items/new" element={
            <ProtectedRoute>
              <ItemNewPage />
            </ProtectedRoute>
          } />
          
          <Route path="items/:id/edit" element={
            <ProtectedRoute>
              <ItemEditPage />
            </ProtectedRoute>
          } />

          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}