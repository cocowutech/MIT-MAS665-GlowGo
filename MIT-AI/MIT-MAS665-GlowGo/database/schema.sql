-- ============================================================================
-- GlowGo MVP Database Schema
-- Supabase PostgreSQL Migration Script
-- ============================================================================
-- 
-- Instructions:
-- 1. Open Supabase Dashboard (https://app.supabase.com)
-- 2. Select your project
-- 3. Go to SQL Editor → New Query
-- 4. Copy and paste this entire script
-- 5. Click "Run" to execute
-- 6. Verify with: SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
--
-- ============================================================================

-- Enable UUID extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- DROP TABLES (for clean migration - use with caution in production)
-- ============================================================================

DROP TABLE IF EXISTS booking_preferences CASCADE;
DROP TABLE IF EXISTS bookings CASCADE;
DROP TABLE IF EXISTS services CASCADE;
DROP TABLE IF EXISTS merchants CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ============================================================================
-- TABLE: users (Customers)
-- ============================================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    google_id VARCHAR(255) UNIQUE,
    profile_photo_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_google_id ON users(google_id);

-- ============================================================================
-- TABLE: merchants (Service Providers/Artisans)
-- ============================================================================

CREATE TABLE merchants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    location_lat FLOAT,
    location_lon FLOAT,
    address VARCHAR(500),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(10),
    service_category VARCHAR(50) NOT NULL CHECK (service_category IN ('haircut', 'nails', 'cleaning', 'massage', 'spa', 'facial', 'waxing', 'makeup')),
    rating FLOAT DEFAULT 0 CHECK (rating >= 0 AND rating <= 5),
    total_reviews INTEGER DEFAULT 0,
    photo_url VARCHAR(500),
    bio TEXT,
    years_experience INTEGER,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for merchants
CREATE INDEX idx_merchants_service_category ON merchants(service_category);
CREATE INDEX idx_merchants_rating ON merchants(rating DESC);
CREATE INDEX idx_merchants_city ON merchants(city);

-- ============================================================================
-- TABLE: services
-- ============================================================================

CREATE TABLE services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL REFERENCES merchants(id) ON DELETE CASCADE,
    service_name VARCHAR(255) NOT NULL,
    description TEXT,
    base_price DECIMAL(10, 2) NOT NULL CHECK (base_price >= 0),
    duration_minutes INTEGER NOT NULL CHECK (duration_minutes > 0),
    photo_url VARCHAR(500),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for services
CREATE INDEX idx_services_merchant_id ON services(merchant_id);
CREATE INDEX idx_services_base_price ON services(base_price);
CREATE INDEX idx_services_is_active ON services(is_active);

-- ============================================================================
-- TABLE: bookings
-- ============================================================================

CREATE TABLE bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    merchant_id UUID NOT NULL REFERENCES merchants(id) ON DELETE CASCADE,
    service_id UUID NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    booking_date DATE NOT NULL,
    booking_time_start TIME NOT NULL,
    booking_time_end TIME,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'completed', 'cancelled')),
    base_price DECIMAL(10, 2) NOT NULL,
    discount_percentage FLOAT DEFAULT 0 CHECK (discount_percentage >= 0 AND discount_percentage <= 100),
    final_price DECIMAL(10, 2) NOT NULL,
    style_preference TEXT,
    notes TEXT,
    calendar_event_id VARCHAR(255),
    confirmation_code VARCHAR(20) UNIQUE,
    cancellation_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for bookings
CREATE INDEX idx_bookings_user_id ON bookings(user_id);
CREATE INDEX idx_bookings_merchant_id ON bookings(merchant_id);
CREATE INDEX idx_bookings_service_id ON bookings(service_id);
CREATE INDEX idx_bookings_booking_date ON bookings(booking_date);
CREATE INDEX idx_bookings_status ON bookings(status);
CREATE INDEX idx_bookings_confirmation_code ON bookings(confirmation_code);

-- ============================================================================
-- TABLE: booking_preferences
-- ============================================================================

CREATE TABLE booking_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    service_type VARCHAR(50),
    budget_min DECIMAL(10, 2),
    budget_max DECIMAL(10, 2),
    time_urgency VARCHAR(20) CHECK (time_urgency IN ('ASAP', 'today', 'week', 'flexible')),
    artisan_preference TEXT,
    special_notes TEXT,
    conversation_history JSONB,
    ready_to_match BOOLEAN DEFAULT false,
    matched_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for booking_preferences
CREATE INDEX idx_booking_preferences_user_id ON booking_preferences(user_id);
CREATE INDEX idx_booking_preferences_ready_to_match ON booking_preferences(ready_to_match);

-- ============================================================================
-- TRIGGERS: Auto-update updated_at timestamp
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_merchants_updated_at BEFORE UPDATE ON merchants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_services_updated_at BEFORE UPDATE ON services
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bookings_updated_at BEFORE UPDATE ON bookings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_booking_preferences_updated_at BEFORE UPDATE ON booking_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- SEED DATA: Users
-- ============================================================================

INSERT INTO users (email, phone, first_name, last_name, google_id, profile_photo_url) VALUES
('john.doe@example.com', '+1-555-0101', 'John', 'Doe', 'google_123456789', 'https://i.pravatar.cc/150?img=12'),
('jane.smith@example.com', '+1-555-0102', 'Jane', 'Smith', 'google_987654321', 'https://i.pravatar.cc/150?img=5'),
('mike.wilson@example.com', '+1-555-0103', 'Mike', 'Wilson', NULL, 'https://i.pravatar.cc/150?img=33');

-- ============================================================================
-- SEED DATA: Merchants
-- ============================================================================

INSERT INTO merchants (
    business_name, 
    email, 
    phone, 
    location_lat, 
    location_lon, 
    address,
    city,
    state,
    zip_code,
    service_category, 
    rating, 
    total_reviews, 
    photo_url, 
    bio,
    years_experience,
    is_verified
) VALUES
(
    'Sarah''s Cuts',
    'contact@sarahscuts.com',
    '+1-555-1001',
    40.7580,
    -73.9855,
    '123 Madison Avenue',
    'New York',
    'NY',
    '10016',
    'haircut',
    4.9,
    542,
    'https://images.unsplash.com/photo-1560066984-138dadb4c035?w=400',
    'Award-winning hair stylist with 15 years of experience. Specializing in modern cuts and color treatments. Featured in Vogue and Elle.',
    15,
    true
),
(
    'Luxe Nails Studio',
    'hello@luxenails.com',
    '+1-555-1002',
    40.7614,
    -73.9776,
    '456 5th Avenue',
    'New York',
    'NY',
    '10018',
    'nails',
    4.8,
    389,
    'https://images.unsplash.com/photo-1604654894610-df63bc536371?w=400',
    'Premium nail care studio offering manicures, pedicures, and nail art. We use only organic, non-toxic products.',
    8,
    true
),
(
    'Wellness Spa & Massage',
    'info@wellnessspa.com',
    '+1-555-1003',
    40.7489,
    -73.9680,
    '789 Park Avenue',
    'New York',
    'NY',
    '10021',
    'massage',
    4.7,
    215,
    'https://images.unsplash.com/photo-1544161515-4ab6ce6db874?w=400',
    'Tranquil spa offering therapeutic massages, facials, and body treatments. Our licensed therapists provide personalized care.',
    10,
    true
),
(
    'Glow Facial Bar',
    'contact@glowfacialbar.com',
    '+1-555-1004',
    40.7282,
    -74.0776,
    '321 Greenwich Street',
    'New York',
    'NY',
    '10007',
    'facial',
    4.9,
    178,
    'https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?w=400',
    'Modern facial bar specializing in custom skincare treatments. Using cutting-edge technology and premium products.',
    6,
    true
),
(
    'Bella Beauty Lounge',
    'hello@bellalounge.com',
    '+1-555-1005',
    40.7549,
    -73.9840,
    '555 Broadway',
    'New York',
    'NY',
    '10012',
    'makeup',
    4.8,
    294,
    'https://images.unsplash.com/photo-1487412947147-5cebf100ffc2?w=400',
    'Professional makeup artists for all occasions. Bridal, special events, photoshoots, and makeup lessons.',
    12,
    true
);

-- ============================================================================
-- SEED DATA: Services
-- ============================================================================

INSERT INTO services (merchant_id, service_name, description, base_price, duration_minutes, photo_url) VALUES
-- Sarah's Cuts services
(
    (SELECT id FROM merchants WHERE business_name = 'Sarah''s Cuts'),
    'Classic Haircut',
    'Professional haircut with wash, cut, and style. Includes consultation.',
    45.00,
    30,
    'https://images.unsplash.com/photo-1562322140-8baeececf3df?w=400'
),
(
    (SELECT id FROM merchants WHERE business_name = 'Sarah''s Cuts'),
    'Hair Color & Highlights',
    'Full color service or highlights. Includes toner and style.',
    125.00,
    120,
    'https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=400'
),
(
    (SELECT id FROM merchants WHERE business_name = 'Sarah''s Cuts'),
    'Blowout & Style',
    'Wash and professional blowout with styling.',
    35.00,
    45,
    'https://images.unsplash.com/photo-1580618672591-eb180b1a973f?w=400'
),
-- Luxe Nails services
(
    (SELECT id FROM merchants WHERE business_name = 'Luxe Nails Studio'),
    'Signature Manicure',
    'Classic manicure with nail shaping, cuticle care, and polish.',
    35.00,
    45,
    'https://images.unsplash.com/photo-1610992015732-2449b76344bc?w=400'
),
(
    (SELECT id FROM merchants WHERE business_name = 'Luxe Nails Studio'),
    'Deluxe Pedicure',
    'Spa pedicure with exfoliation, massage, and polish.',
    50.00,
    60,
    'https://images.unsplash.com/photo-1519014816548-bf5fe059798b?w=400'
),
(
    (SELECT id FROM merchants WHERE business_name = 'Luxe Nails Studio'),
    'Gel Manicure',
    'Long-lasting gel polish manicure.',
    45.00,
    45,
    'https://images.unsplash.com/photo-1632345031435-8727f6897d53?w=400'
),
-- Wellness Spa services
(
    (SELECT id FROM merchants WHERE business_name = 'Wellness Spa & Massage'),
    'Swedish Massage',
    'Relaxing full-body massage with gentle pressure.',
    90.00,
    60,
    'https://images.unsplash.com/photo-1544161515-4ab6ce6db874?w=400'
),
(
    (SELECT id FROM merchants WHERE business_name = 'Wellness Spa & Massage'),
    'Deep Tissue Massage',
    'Therapeutic massage targeting muscle tension and knots.',
    110.00,
    60,
    'https://images.unsplash.com/photo-1519823551278-64ac92734fb1?w=400'
),
(
    (SELECT id FROM merchants WHERE business_name = 'Wellness Spa & Massage'),
    'Hot Stone Massage',
    'Luxurious massage with heated stones for deep relaxation.',
    130.00,
    90,
    'https://images.unsplash.com/photo-1540555700478-4be289fbecef?w=400'
),
-- Glow Facial Bar services
(
    (SELECT id FROM merchants WHERE business_name = 'Glow Facial Bar'),
    'Signature Glow Facial',
    'Custom facial with deep cleansing, exfoliation, and hydration.',
    85.00,
    60,
    'https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?w=400'
),
(
    (SELECT id FROM merchants WHERE business_name = 'Glow Facial Bar'),
    'Anti-Aging Treatment',
    'Advanced facial targeting fine lines and wrinkles.',
    120.00,
    75,
    'https://images.unsplash.com/photo-1516975080664-ed2fc6a32937?w=400'
),
-- Bella Beauty Lounge services
(
    (SELECT id FROM merchants WHERE business_name = 'Bella Beauty Lounge'),
    'Bridal Makeup',
    'Complete bridal makeup with trial session.',
    150.00,
    90,
    'https://images.unsplash.com/photo-1487412947147-5cebf100ffc2?w=400'
),
(
    (SELECT id FROM merchants WHERE business_name = 'Bella Beauty Lounge'),
    'Special Event Makeup',
    'Professional makeup for any special occasion.',
    75.00,
    60,
    'https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=400'
);

-- ============================================================================
-- SEED DATA: Bookings
-- ============================================================================

INSERT INTO bookings (
    user_id,
    merchant_id,
    service_id,
    booking_date,
    booking_time_start,
    booking_time_end,
    status,
    base_price,
    discount_percentage,
    final_price,
    style_preference,
    notes,
    confirmation_code
) VALUES
-- John's confirmed haircut
(
    (SELECT id FROM users WHERE email = 'john.doe@example.com'),
    (SELECT id FROM merchants WHERE business_name = 'Sarah''s Cuts'),
    (SELECT id FROM services WHERE service_name = 'Classic Haircut'),
    CURRENT_DATE + INTERVAL '3 days',
    '14:00:00',
    '14:30:00',
    'confirmed',
    45.00,
    0,
    45.00,
    'Short fade on sides, textured on top',
    'First time customer',
    'GG-HC-001'
),
-- Jane's pending pedicure
(
    (SELECT id FROM users WHERE email = 'jane.smith@example.com'),
    (SELECT id FROM merchants WHERE business_name = 'Luxe Nails Studio'),
    (SELECT id FROM services WHERE service_name = 'Deluxe Pedicure'),
    CURRENT_DATE + INTERVAL '5 days',
    '11:00:00',
    '12:00:00',
    'pending',
    50.00,
    10,
    45.00,
    NULL,
    'Prefer light pink polish',
    'GG-NL-002'
),
-- Mike's completed massage
(
    (SELECT id FROM users WHERE email = 'mike.wilson@example.com'),
    (SELECT id FROM merchants WHERE business_name = 'Wellness Spa & Massage'),
    (SELECT id FROM services WHERE service_name = 'Swedish Massage'),
    CURRENT_DATE - INTERVAL '2 days',
    '16:00:00',
    '17:00:00',
    'completed',
    90.00,
    0,
    90.00,
    NULL,
    'Focus on lower back',
    'GG-MS-003'
);

-- ============================================================================
-- SEED DATA: Booking Preferences
-- ============================================================================

INSERT INTO booking_preferences (
    user_id,
    service_type,
    budget_min,
    budget_max,
    time_urgency,
    artisan_preference,
    special_notes,
    conversation_history,
    ready_to_match
) VALUES
(
    (SELECT id FROM users WHERE email = 'john.doe@example.com'),
    'haircut',
    30.00,
    60.00,
    'week',
    'Experienced stylist, any gender',
    'Looking for modern, professional cut',
    '{"messages": [{"role": "assistant", "content": "What type of service are you looking for?"}, {"role": "user", "content": "I need a haircut"}]}'::jsonb,
    true
),
(
    (SELECT id FROM users WHERE email = 'jane.smith@example.com'),
    'facial',
    50.00,
    100.00,
    'flexible',
    'Female provider preferred',
    'Sensitive skin, prefer organic products',
    '{"messages": [{"role": "assistant", "content": "What brings you here today?"}, {"role": "user", "content": "Looking for a facial treatment"}]}'::jsonb,
    false
);

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Run these queries to verify the data was inserted correctly:

-- Check table counts
SELECT 'users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'merchants', COUNT(*) FROM merchants
UNION ALL
SELECT 'services', COUNT(*) FROM services
UNION ALL
SELECT 'bookings', COUNT(*) FROM bookings
UNION ALL
SELECT 'booking_preferences', COUNT(*) FROM booking_preferences;

-- View all merchants with their service counts
SELECT 
    m.business_name,
    m.service_category,
    m.rating,
    m.total_reviews,
    COUNT(s.id) as service_count
FROM merchants m
LEFT JOIN services s ON m.id = s.merchant_id
GROUP BY m.id, m.business_name, m.service_category, m.rating, m.total_reviews
ORDER BY m.rating DESC;

-- View upcoming bookings
SELECT 
    u.first_name || ' ' || u.last_name as customer,
    m.business_name as merchant,
    s.service_name,
    b.booking_date,
    b.booking_time_start,
    b.status,
    b.final_price
FROM bookings b
JOIN users u ON b.user_id = u.id
JOIN merchants m ON b.merchant_id = m.id
JOIN services s ON b.service_id = s.id
WHERE b.booking_date >= CURRENT_DATE
ORDER BY b.booking_date, b.booking_time_start;

-- ============================================================================
-- SUCCESS!
-- ============================================================================
-- 
-- If you see no errors above, your database is ready! 🎉
--
-- Expected counts:
-- - users: 3
-- - merchants: 5
-- - services: 13
-- - bookings: 3
-- - booking_preferences: 2
--
-- Next steps:
-- 1. Update your backend DATABASE_URL in .env
-- 2. Create SQLAlchemy models matching this schema
-- 3. Test API connections
--
-- ============================================================================


