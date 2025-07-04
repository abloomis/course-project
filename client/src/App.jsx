import {Routes, Route} from 'react-router-dom';

// import pages
import HomePage from './pages/HomePage';
import TutorialsPage from './pages/Tutorialspage';
import FAQPage from './pages/FAQPage';
import ImportPage from './pages/ImportPage';
import EditPage from './pages/EditPage';

// import navigation function for routing
import Navigation from './components/Navigation.jsx';

function App() {
// establish the page routing
  return (
    
    <div className="app">

      {/* this header is shown on all pages */}
      <header>
        <h1>Ranking Tool</h1>
      </header>

      <Routes>
        <Route path='/' element={<HomePage />} />
        <Route path='/import' element={<ImportPage />} />
        <Route path='/faq' element={<FAQPage />} />
        <Route path='/tutorials' element={<TutorialsPage />} />
        <Route path='/edit' element={<EditPage />} />
      </Routes>
      
      {/* navigation options for tutorials + faq is shown on all pages */}
      <Navigation/>

      {/* this footer is shown on all pages */}
      <footer>
        <p> © 2025 alex loomis</p>
      </footer>
    </div>
      
  );
}

export default App;