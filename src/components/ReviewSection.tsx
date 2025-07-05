import React, { useState, useEffect } from 'react';
import { Star, MessageCircle, ThumbsUp, User } from 'lucide-react';

interface Review {
  id: number;
  hotelId: number;
  hotelName: string;
  userName: string;
  rating: number;
  comment: string;
  date: string;
  likes: number;
}

const ReviewSection: React.FC = () => {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [newReview, setNewReview] = useState({
    hotelId: 1,
    rating: 5,
    comment: ''
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchReviews();
  }, []);

  const fetchReviews = async () => {
    try {
      // In real implementation: await fetch('http://localhost:84/api/reviews')
      const mockReviews: Review[] = [
        {
          id: 1,
          hotelId: 1,
          hotelName: "Grand Palace Hotel",
          userName: "Sarah Johnson",
          rating: 5,
          comment: "Amazing stay! The service was exceptional and the room was beautiful. Will definitely come back.",
          date: "2024-01-15",
          likes: 12
        },
        {
          id: 2,
          hotelId: 2,
          hotelName: "Oceanview Resort",
          userName: "Mike Chen",
          rating: 4,
          comment: "Great location with stunning ocean views. The breakfast was fantastic, though the WiFi could be better.",
          date: "2024-01-10",
          likes: 8
        },
        {
          id: 3,
          hotelId: 3,
          hotelName: "Mountain Lodge",
          userName: "Emily Davis",
          rating: 5,
          comment: "Perfect for our mountain getaway. The staff was friendly and the hiking trails were amazing.",
          date: "2024-01-08",
          likes: 15
        }
      ];
      
      setTimeout(() => {
        setReviews(mockReviews);
        setLoading(false);
      }, 1000);
    } catch (error) {
      console.error('Error fetching reviews:', error);
      setLoading(false);
    }
  };

  const handleSubmitReview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newReview.comment.trim()) {
      alert('Please write a review comment');
      return;
    }

    try {
      // In real implementation: await fetch('http://localhost:84/api/reviews', {...})
      const review: Review = {
        id: Date.now(),
        hotelId: newReview.hotelId,
        hotelName: "Grand Palace Hotel", // This would come from the hotel service
        userName: "Current User",
        rating: newReview.rating,
        comment: newReview.comment,
        date: new Date().toISOString().split('T')[0],
        likes: 0
      };

      setReviews(prev => [review, ...prev]);
      setNewReview({ hotelId: 1, rating: 5, comment: '' });
      alert('Review submitted successfully!');
    } catch (error) {
      console.error('Error submitting review:', error);
    }
  };

  const handleLike = (reviewId: number) => {
    setReviews(prev => prev.map(review => 
      review.id === reviewId 
        ? { ...review, likes: review.likes + 1 }
        : review
    ));
  };

  const renderStars = (rating: number, interactive: boolean = false, onChange?: (rating: number) => void) => {
    return (
      <div className="flex space-x-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`h-5 w-5 ${
              star <= rating 
                ? 'text-yellow-400 fill-current' 
                : 'text-gray-300'
            } ${interactive ? 'cursor-pointer hover:text-yellow-400' : ''}`}
            onClick={() => interactive && onChange && onChange(star)}
          />
        ))}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Hotel Reviews</h2>
        
        {/* Submit Review Form */}
        <div className="bg-gray-50 rounded-lg p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Write a Review</h3>
          <form onSubmit={handleSubmitReview} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Select Hotel</label>
              <select
                value={newReview.hotelId}
                onChange={(e) => setNewReview(prev => ({ ...prev, hotelId: parseInt(e.target.value) }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={1}>Grand Palace Hotel</option>
                <option value={2}>Oceanview Resort</option>
                <option value={3}>Mountain Lodge</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Rating</label>
              {renderStars(newReview.rating, true, (rating) => 
                setNewReview(prev => ({ ...prev, rating }))
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Your Review</label>
              <textarea
                value={newReview.comment}
                onChange={(e) => setNewReview(prev => ({ ...prev, comment: e.target.value }))}
                placeholder="Share your experience..."
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <button
              type="submit"
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Submit Review
            </button>
          </form>
        </div>

        {/* Reviews List */}
        <div className="space-y-4">
          {reviews.map((review) => (
            <div key={review.id} className="border border-gray-200 rounded-lg p-6">
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-center space-x-3">
                  <div className="bg-blue-100 w-10 h-10 rounded-full flex items-center justify-center">
                    <User className="h-5 w-5 text-blue-600" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900">{review.userName}</h4>
                    <p className="text-sm text-gray-600">{review.hotelName}</p>
                  </div>
                </div>
                <div className="text-right">
                  {renderStars(review.rating)}
                  <p className="text-sm text-gray-500 mt-1">{review.date}</p>
                </div>
              </div>

              <p className="text-gray-700 mb-4">{review.comment}</p>

              <div className="flex items-center justify-between">
                <button
                  onClick={() => handleLike(review.id)}
                  className="flex items-center space-x-2 text-gray-500 hover:text-blue-600 transition-colors"
                >
                  <ThumbsUp className="h-4 w-4" />
                  <span className="text-sm">{review.likes} likes</span>
                </button>
                <button className="flex items-center space-x-2 text-gray-500 hover:text-blue-600 transition-colors">
                  <MessageCircle className="h-4 w-4" />
                  <span className="text-sm">Reply</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ReviewSection;