import {Routes,Route} from 'react-router-dom';
import HomePage from './pages/HomePage';
import ImportPage from './pages/ImportPage';
import FAQPage from './pages/FAQPage';

function App() {
  return (
    <Routes>
      <Route path='/' element={<HomePage />} />
      <Route path='/import' element={<ImportPage />} />
      <Route path='/faq' element={<FAQPage />} />
    </Routes>
  );
}

export default App;