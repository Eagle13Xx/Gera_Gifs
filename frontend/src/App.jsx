// src/App.jsx

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Header } from './components/layout/Header';
import { Footer } from './components/layout/Footer';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import PlansPage from './pages/PlansPage';
import ProfilePage from './pages/ProfilePage';
import PaymentStatusPage from './pages/PaymentStatusPage';

function App() {
  return (
    // <AccessibilityProvider>
    //   <AuthProvider>
    //     <SubscriptionProvider>
          <Router>
            <div className="app">
              <Header />
              <main className="main-content">
                <Routes>
                  <Route path="/" element={<HomePage />} />
                  <Route path="/login" element={<LoginPage />} />
                  <Route path="/plans" element={<PlansPage />} />
                  <Route path="/profile" element={<ProfilePage />} />
                    <Route path="/payment/status" element={<PaymentStatusPage />} />
                </Routes>
              </main>
              <Footer />
            </div>
          </Router>
    //     </SubscriptionProvider>
    //   </AuthProvider>
    // </AccessibilityProvider>
  );
}

export default App;