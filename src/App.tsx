import React, { useState } from 'react';
import { Hotel, User, Calendar, Star, CreditCard, Settings } from 'lucide-react';
import HotelListing from './components/HotelListing';
import BookingForm from './components/BookingForm';
import UserLogin from './components/UserLogin';
import ReviewSection from './components/ReviewSection';
import PaymentForm from './components/PaymentForm';
import AdminDashboard from './components/AdminDashboard';

function App() {
  const [activeTab, setActiveTab] = useState('hotels');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [selectedHotel, setSelectedHotel] = useState(null);

  const navItems = [
    { id: 'hotels', label: 'Hotels', icon: Hotel },
    { id: 'booking', label: 'Booking', icon: Calendar },
    { id: 'reviews', label: 'Reviews', icon: Star },
    { id: 'payment', label: 'Payment', icon: CreditCard },
  ];

  const renderContent = () => {
    if (!isLoggedIn) {
      return <UserLogin onLogin={setIsLoggedIn} onAdminLogin={setIsAdmin} />;
    }

    if (isAdmin) {
      return <AdminDashboard />;
    }

    switch (activeTab) {
      case 'hotels':
        return <HotelListing onSelectHotel={setSelectedHotel} />;
      case 'booking':
        return <BookingForm selectedHotel={selectedHotel} />;
      case 'reviews':
        return <ReviewSection />;
      case 'payment':
        return <PaymentForm />;
      default:
        return <HotelListing onSelectHotel={setSelectedHotel} />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-emerald-50">
      <header className="bg-white shadow-lg border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <Hotel className="h-8 w-8 text-blue-600" />
              <h1 className="text-2xl font-bold text-gray-900">LuxeStay</h1>
            </div>
            <div className="flex items-center space-x-4">
              {isLoggedIn && (
                <>
                  <span className="text-sm text-gray-600">
                    Welcome, {isAdmin ? 'Admin' : 'Guest'}
                  </span>
                  <button
                    onClick={() => {
                      setIsLoggedIn(false);
                      setIsAdmin(false);
                      setActiveTab('hotels');
                    }}
                    className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition-colors"
                  >
                    Logout
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </header>

      {isLoggedIn && !isAdmin && (
        <nav className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex space-x-8">
              {navItems.map((item) => {
                const Icon = item.icon;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    className={`flex items-center space-x-2 py-4 px-3 border-b-2 font-medium text-sm transition-colors ${
                      activeTab === item.id
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <Icon className="h-5 w-5" />
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </nav>
      )}

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {renderContent()}
      </main>
    </div>
  );
}

export default App;