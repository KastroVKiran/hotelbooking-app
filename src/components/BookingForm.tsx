import React, { useState } from 'react';
import { Calendar, Users, Clock, CheckCircle } from 'lucide-react';

interface Hotel {
  id: number;
  name: string;
  location: string;
  price: number;
  image: string;
}

interface BookingFormProps {
  selectedHotel: Hotel | null;
}

const BookingForm: React.FC<BookingFormProps> = ({ selectedHotel }) => {
  const [formData, setFormData] = useState({
    checkIn: '',
    checkOut: '',
    guests: 1,
    roomType: 'standard',
    specialRequests: ''
  });
  const [availableRooms, setAvailableRooms] = useState<number>(0);
  const [loading, setLoading] = useState(false);
  const [bookingConfirmed, setBookingConfirmed] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const checkAvailability = async () => {
    if (!formData.checkIn || !formData.checkOut) {
      alert('Please select check-in and check-out dates');
      return;
    }
    
    setLoading(true);
    try {
      // In real implementation: await fetch('http://localhost:82/api/availability', {...})
      setTimeout(() => {
        setAvailableRooms(Math.floor(Math.random() * 10) + 1);
        setLoading(false);
      }, 1000);
    } catch (error) {
      console.error('Error checking availability:', error);
      setLoading(false);
    }
  };

  const handleBooking = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedHotel || availableRooms === 0) {
      alert('Please select a hotel and check availability first');
      return;
    }

    setLoading(true);
    try {
      // In real implementation: await fetch('http://localhost:82/api/bookings', {...})
      setTimeout(() => {
        setBookingConfirmed(true);
        setLoading(false);
      }, 1500);
    } catch (error) {
      console.error('Error creating booking:', error);
      setLoading(false);
    }
  };

  const calculateNights = () => {
    if (!formData.checkIn || !formData.checkOut) return 0;
    const checkIn = new Date(formData.checkIn);
    const checkOut = new Date(formData.checkOut);
    const diffTime = Math.abs(checkOut.getTime() - checkIn.getTime());
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  };

  const calculateTotal = () => {
    if (!selectedHotel) return 0;
    return selectedHotel.price * calculateNights();
  };

  if (bookingConfirmed) {
    return (
      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-8 text-center">
        <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Booking Confirmed!</h2>
        <p className="text-gray-600 mb-4">
          Your reservation at {selectedHotel?.name} has been successfully booked.
        </p>
        <div className="bg-gray-50 rounded-lg p-4 mb-4">
          <h3 className="font-semibold text-gray-900 mb-2">Booking Details</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Check-in:</span>
              <span className="font-medium ml-2">{formData.checkIn}</span>
            </div>
            <div>
              <span className="text-gray-600">Check-out:</span>
              <span className="font-medium ml-2">{formData.checkOut}</span>
            </div>
            <div>
              <span className="text-gray-600">Guests:</span>
              <span className="font-medium ml-2">{formData.guests}</span>
            </div>
            <div>
              <span className="text-gray-600">Total:</span>
              <span className="font-medium ml-2">${calculateTotal()}</span>
            </div>
          </div>
        </div>
        <button
          onClick={() => {
            setBookingConfirmed(false);
            setFormData({
              checkIn: '',
              checkOut: '',
              guests: 1,
              roomType: 'standard',
              specialRequests: ''
            });
            setAvailableRooms(0);
          }}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Make Another Booking
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {selectedHotel && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Book Your Stay</h2>
          <div className="flex items-center space-x-4 mb-6">
            <img
              src={selectedHotel.image}
              alt={selectedHotel.name}
              className="w-24 h-24 object-cover rounded-lg"
            />
            <div>
              <h3 className="text-xl font-semibold text-gray-900">{selectedHotel.name}</h3>
              <p className="text-gray-600">{selectedHotel.location}</p>
              <p className="text-lg font-bold text-green-600">${selectedHotel.price}/night</p>
            </div>
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-md p-6">
        <form onSubmit={handleBooking} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Calendar className="inline h-4 w-4 mr-2" />
                Check-in Date
              </label>
              <input
                type="date"
                name="checkIn"
                value={formData.checkIn}
                onChange={handleInputChange}
                min={new Date().toISOString().split('T')[0]}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Calendar className="inline h-4 w-4 mr-2" />
                Check-out Date
              </label>
              <input
                type="date"
                name="checkOut"
                value={formData.checkOut}
                onChange={handleInputChange}
                min={formData.checkIn || new Date().toISOString().split('T')[0]}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Users className="inline h-4 w-4 mr-2" />
                Number of Guests
              </label>
              <select
                name="guests"
                value={formData.guests}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {[1, 2, 3, 4, 5, 6].map(num => (
                  <option key={num} value={num}>{num} Guest{num > 1 ? 's' : ''}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Room Type</label>
              <select
                name="roomType"
                value={formData.roomType}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="standard">Standard Room</option>
                <option value="deluxe">Deluxe Room</option>
                <option value="suite">Suite</option>
                <option value="presidential">Presidential Suite</option>
              </select>
            </div>
          </div>

          <div className="flex space-x-4">
            <button
              type="button"
              onClick={checkAvailability}
              disabled={loading}
              className="bg-emerald-600 text-white px-6 py-3 rounded-lg hover:bg-emerald-700 transition-colors disabled:opacity-50"
            >
              {loading ? 'Checking...' : 'Check Availability'}
            </button>
            {availableRooms > 0 && (
              <div className="flex items-center space-x-2 text-green-600">
                <CheckCircle className="h-5 w-5" />
                <span className="font-medium">{availableRooms} rooms available</span>
              </div>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Special Requests</label>
            <textarea
              name="specialRequests"
              value={formData.specialRequests}
              onChange={handleInputChange}
              rows={3}
              placeholder="Any special requests or preferences..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {formData.checkIn && formData.checkOut && selectedHotel && (
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-2">Booking Summary</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Nights:</span>
                  <span className="font-medium ml-2">{calculateNights()}</span>
                </div>
                <div>
                  <span className="text-gray-600">Price per night:</span>
                  <span className="font-medium ml-2">${selectedHotel.price}</span>
                </div>
                <div>
                  <span className="text-gray-600">Total:</span>
                  <span className="font-bold text-lg ml-2">${calculateTotal()}</span>
                </div>
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={loading || availableRooms === 0}
            className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Processing...' : 'Confirm Booking'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default BookingForm;