import React, { useState, useEffect } from 'react';
import { MapPin, Wifi, Car, Utensils, Star, Users } from 'lucide-react';

interface Hotel {
  id: number;
  name: string;
  location: string;
  rating: number;
  price: number;
  image: string;
  amenities: string[];
  rooms: number;
  description: string;
}

interface HotelListingProps {
  onSelectHotel: (hotel: Hotel) => void;
}

const HotelListing: React.FC<HotelListingProps> = ({ onSelectHotel }) => {
  const [hotels, setHotels] = useState<Hotel[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedLocation, setSelectedLocation] = useState('');

  useEffect(() => {
    // Simulate API call to hotel service (port 81)
    const fetchHotels = async () => {
      try {
        // In real implementation, this would be: await fetch('http://localhost:81/api/hotels')
        const mockHotels: Hotel[] = [
          {
            id: 1,
            name: "Grand Palace Hotel",
            location: "New York, NY",
            rating: 4.8,
            price: 299,
            image: "https://images.pexels.com/photos/258154/pexels-photo-258154.jpeg?auto=compress&cs=tinysrgb&w=800",
            amenities: ["WiFi", "Parking", "Restaurant", "Spa"],
            rooms: 150,
            description: "Luxury hotel in the heart of Manhattan with exceptional service."
          },
          {
            id: 2,
            name: "Oceanview Resort",
            location: "Miami, FL",
            rating: 4.6,
            price: 399,
            image: "https://images.pexels.com/photos/2034335/pexels-photo-2034335.jpeg?auto=compress&cs=tinysrgb&w=800",
            amenities: ["WiFi", "Pool", "Beach Access", "Restaurant"],
            rooms: 200,
            description: "Beachfront resort with stunning ocean views and world-class amenities."
          },
          {
            id: 3,
            name: "Mountain Lodge",
            location: "Denver, CO",
            rating: 4.7,
            price: 249,
            image: "https://images.pexels.com/photos/1134176/pexels-photo-1134176.jpeg?auto=compress&cs=tinysrgb&w=800",
            amenities: ["WiFi", "Fireplace", "Hiking", "Restaurant"],
            rooms: 80,
            description: "Cozy mountain retreat perfect for outdoor enthusiasts."
          }
        ];
        
        setTimeout(() => {
          setHotels(mockHotels);
          setLoading(false);
        }, 1000);
      } catch (error) {
        console.error('Error fetching hotels:', error);
        setLoading(false);
      }
    };

    fetchHotels();
  }, []);

  const filteredHotels = hotels.filter(hotel =>
    hotel.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
    (selectedLocation === '' || hotel.location.includes(selectedLocation))
  );

  const getAmenityIcon = (amenity: string) => {
    switch (amenity.toLowerCase()) {
      case 'wifi':
        return <Wifi className="h-4 w-4" />;
      case 'parking':
        return <Car className="h-4 w-4" />;
      case 'restaurant':
        return <Utensils className="h-4 w-4" />;
      default:
        return <Star className="h-4 w-4" />;
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Find Your Perfect Stay</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Search Hotels</label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Enter hotel name..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Location</label>
            <select
              value={selectedLocation}
              onChange={(e) => setSelectedLocation(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Locations</option>
              <option value="New York">New York</option>
              <option value="Miami">Miami</option>
              <option value="Denver">Denver</option>
            </select>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredHotels.map((hotel) => (
          <div key={hotel.id} className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
            <img
              src={hotel.image}
              alt={hotel.name}
              className="w-full h-48 object-cover"
            />
            <div className="p-6">
              <div className="flex justify-between items-start mb-2">
                <h3 className="text-xl font-semibold text-gray-900">{hotel.name}</h3>
                <div className="flex items-center space-x-1">
                  <Star className="h-4 w-4 text-yellow-400 fill-current" />
                  <span className="text-sm text-gray-600">{hotel.rating}</span>
                </div>
              </div>
              <div className="flex items-center space-x-1 text-gray-600 mb-2">
                <MapPin className="h-4 w-4" />
                <span className="text-sm">{hotel.location}</span>
              </div>
              <p className="text-gray-600 text-sm mb-4">{hotel.description}</p>
              
              <div className="flex items-center space-x-2 mb-4">
                <Users className="h-4 w-4 text-gray-500" />
                <span className="text-sm text-gray-600">{hotel.rooms} rooms available</span>
              </div>

              <div className="flex flex-wrap gap-2 mb-4">
                {hotel.amenities.map((amenity) => (
                  <div key={amenity} className="flex items-center space-x-1 bg-gray-100 px-2 py-1 rounded-full">
                    {getAmenityIcon(amenity)}
                    <span className="text-xs text-gray-600">{amenity}</span>
                  </div>
                ))}
              </div>

              <div className="flex justify-between items-center">
                <div>
                  <span className="text-2xl font-bold text-green-600">${hotel.price}</span>
                  <span className="text-sm text-gray-500">/night</span>
                </div>
                <button
                  onClick={() => onSelectHotel(hotel)}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Book Now
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default HotelListing;