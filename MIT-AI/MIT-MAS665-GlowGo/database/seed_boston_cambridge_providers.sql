-- ============================================================================
-- GlowGo Boston/Cambridge Beauty Service Providers Seed Data
-- Realistic provider data for demo and testing
-- ============================================================================
--
-- Run this after:
-- 1. schema.sql (base tables)
-- 2. add_enhanced_merchant_fields.sql (enhanced columns)
--
-- ============================================================================

-- Clear existing merchants and services for fresh seed
DELETE FROM services;
DELETE FROM merchants;

-- ============================================================================
-- BOSTON PROVIDERS
-- ============================================================================

-- 1. Salon Mario Russo - High-end hair salon on Newbury Street
INSERT INTO merchants (
    business_name, email, phone, location_lat, location_lon, address, city, state, zip_code,
    service_category, rating, total_reviews, photo_url, bio, years_experience, is_verified,
    yelp_id, price_range, photos, specialties, stylist_names, booking_url, data_source
) VALUES (
    'Salon Mario Russo',
    'contact@salonmariorusso.com',
    '+1-617-424-6676',
    42.3520, -71.0758,
    '9 Newbury Street',
    'Boston', 'MA', '02116',
    'hair_salon',
    4.8, 423,
    'https://images.unsplash.com/photo-1560066984-138dadb4c035?w=400',
    'Award-winning salon on Newbury Street. Our team of expert stylists specializes in precision cuts, color correction, and balayage. Featured in Boston Magazine Best of Boston.',
    25, true,
    'salon-mario-russo-boston', '$$$',
    '["https://images.unsplash.com/photo-1560066984-138dadb4c035?w=400", "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=400"]'::jsonb,
    ARRAY['Color Specialists', 'Curly Hair Experts', 'Bridal', 'Balayage'],
    ARRAY['Mario Russo', 'Anna Chen', 'David Kim', 'Sarah Mitchell'],
    'https://salonmariorusso.com/book',
    'yelp'
);

-- Services for Salon Mario Russo
INSERT INTO services (merchant_id, service_name, description, base_price, duration_minutes, stylist_name, category) VALUES
((SELECT id FROM merchants WHERE business_name = 'Salon Mario Russo'), 'Women''s Haircut', 'Precision cut with wash and style', 85.00, 45, NULL, 'haircut'),
((SELECT id FROM merchants WHERE business_name = 'Salon Mario Russo'), 'Men''s Haircut', 'Classic or modern cut with styling', 55.00, 30, NULL, 'haircut'),
((SELECT id FROM merchants WHERE business_name = 'Salon Mario Russo'), 'Balayage', 'Hand-painted highlights for natural sun-kissed look', 250.00, 180, NULL, 'color'),
((SELECT id FROM merchants WHERE business_name = 'Salon Mario Russo'), 'Full Highlights', 'Full foil highlights with toner', 200.00, 120, NULL, 'color'),
((SELECT id FROM merchants WHERE business_name = 'Salon Mario Russo'), 'Blowout', 'Professional wash and blowdry', 50.00, 45, NULL, 'styling');

-- 2. G2O Spa + Salon - Luxury spa and salon in Back Bay
INSERT INTO merchants (
    business_name, email, phone, location_lat, location_lon, address, city, state, zip_code,
    service_category, rating, total_reviews, photo_url, bio, years_experience, is_verified,
    yelp_id, price_range, photos, specialties, stylist_names, booking_url, data_source
) VALUES (
    'G2O Spa + Salon',
    'hello@g2ospa.com',
    '+1-617-262-2220',
    42.3487, -71.0759,
    '35 Exeter Street',
    'Boston', 'MA', '02116',
    'spa',
    4.7, 312,
    'https://images.unsplash.com/photo-1580618672591-eb180b1a973f?w=400',
    'Full-service spa and salon in the heart of Back Bay. Offering hair, nails, massage, and skincare services in a luxurious, relaxing environment.',
    15, true,
    'g2o-spa-salon-boston', '$$$',
    '["https://images.unsplash.com/photo-1580618672591-eb180b1a973f?w=400"]'::jsonb,
    ARRAY['Spa Services', 'Hair Extensions', 'Keratin Treatments', 'Bridal'],
    ARRAY['Jennifer Walsh', 'Michael Torres', 'Sarah Miller'],
    'https://g2ospa.com/appointments',
    'yelp'
);

-- Services for G2O Spa + Salon
INSERT INTO services (merchant_id, service_name, description, base_price, duration_minutes, stylist_name, category) VALUES
((SELECT id FROM merchants WHERE business_name = 'G2O Spa + Salon'), 'Haircut & Style', 'Cut with wash and style', 75.00, 60, NULL, 'haircut'),
((SELECT id FROM merchants WHERE business_name = 'G2O Spa + Salon'), 'Keratin Treatment', 'Smoothing treatment for frizz-free hair', 350.00, 180, NULL, 'treatment'),
((SELECT id FROM merchants WHERE business_name = 'G2O Spa + Salon'), 'Deep Conditioning', 'Intensive moisture treatment', 45.00, 30, NULL, 'treatment'),
((SELECT id FROM merchants WHERE business_name = 'G2O Spa + Salon'), 'Swedish Massage', 'Full body relaxation massage', 145.00, 60, NULL, 'massage'),
((SELECT id FROM merchants WHERE business_name = 'G2O Spa + Salon'), 'Deep Tissue Massage', 'Therapeutic deep pressure massage', 165.00, 60, NULL, 'massage');

-- 3. Polished Nail Lounge - Premium nail salon on Newbury
INSERT INTO merchants (
    business_name, email, phone, location_lat, location_lon, address, city, state, zip_code,
    service_category, rating, total_reviews, photo_url, bio, years_experience, is_verified,
    yelp_id, price_range, photos, specialties, stylist_names, booking_url, data_source
) VALUES (
    'Polished Nail Lounge',
    'info@polishednaillounge.com',
    '+1-617-267-0711',
    42.3481, -71.0865,
    '355 Newbury Street',
    'Boston', 'MA', '02115',
    'nail_salon',
    4.6, 234,
    'https://images.unsplash.com/photo-1604654894610-df63bc536371?w=400',
    'Upscale nail salon offering manicures, pedicures, and nail art. We use only non-toxic, organic products for a healthier beauty experience.',
    8, true,
    'polished-nail-lounge-boston', '$$',
    '["https://images.unsplash.com/photo-1604654894610-df63bc536371?w=400"]'::jsonb,
    ARRAY['Nail Art', 'Organic Products', 'Bridal Nails', 'Gel Extensions'],
    ARRAY['Lisa Nguyen', 'Emily Zhang', 'Michelle Lee'],
    'https://polishednaillounge.com/appointments',
    'yelp'
);

-- Services for Polished Nail Lounge
INSERT INTO services (merchant_id, service_name, description, base_price, duration_minutes, stylist_name, category) VALUES
((SELECT id FROM merchants WHERE business_name = 'Polished Nail Lounge'), 'Classic Manicure', 'Nail shaping, cuticle care, and polish', 30.00, 30, NULL, 'manicure'),
((SELECT id FROM merchants WHERE business_name = 'Polished Nail Lounge'), 'Gel Manicure', 'Long-lasting gel polish manicure', 45.00, 45, NULL, 'manicure'),
((SELECT id FROM merchants WHERE business_name = 'Polished Nail Lounge'), 'Spa Pedicure', 'Soak, scrub, massage, and polish', 55.00, 60, NULL, 'pedicure'),
((SELECT id FROM merchants WHERE business_name = 'Polished Nail Lounge'), 'Nail Art', 'Custom nail art designs', 15.00, 20, NULL, 'add-on');

-- 4. Exhale Spa Back Bay - Wellness and spa
INSERT INTO merchants (
    business_name, email, phone, location_lat, location_lon, address, city, state, zip_code,
    service_category, rating, total_reviews, photo_url, bio, years_experience, is_verified,
    yelp_id, price_range, photos, specialties, stylist_names, booking_url, data_source
) VALUES (
    'Exhale Spa Back Bay',
    'backbay@exhalespa.com',
    '+1-617-532-7000',
    42.3537, -71.0704,
    '28 Arlington Street',
    'Boston', 'MA', '02116',
    'spa',
    4.8, 678,
    'https://images.unsplash.com/photo-1544161515-4ab6ce6db874?w=400',
    'Mind-body spa offering massage, facials, and wellness classes. Our expert therapists provide personalized treatments for ultimate relaxation and rejuvenation.',
    12, true,
    'exhale-spa-back-bay-boston', '$$$$',
    '["https://images.unsplash.com/photo-1544161515-4ab6ce6db874?w=400"]'::jsonb,
    ARRAY['Therapeutic Massage', 'Facials', 'Wellness', 'Yoga Classes'],
    ARRAY['Dr. Sarah Kim', 'Jessica Brown', 'Amanda White', 'Tom Chen'],
    'https://exhalespa.com/book',
    'yelp'
);

-- Services for Exhale Spa
INSERT INTO services (merchant_id, service_name, description, base_price, duration_minutes, stylist_name, category) VALUES
((SELECT id FROM merchants WHERE business_name = 'Exhale Spa Back Bay'), 'Swedish Massage', 'Classic relaxation massage', 145.00, 60, NULL, 'massage'),
((SELECT id FROM merchants WHERE business_name = 'Exhale Spa Back Bay'), 'Deep Tissue Massage', 'Targeted muscle relief', 165.00, 60, NULL, 'massage'),
((SELECT id FROM merchants WHERE business_name = 'Exhale Spa Back Bay'), 'Signature Facial', 'Custom facial treatment', 185.00, 75, NULL, 'facial'),
((SELECT id FROM merchants WHERE business_name = 'Exhale Spa Back Bay'), 'Body Scrub', 'Exfoliating body treatment', 125.00, 45, NULL, 'body');

-- 5. Acote Salon - High-end color specialists
INSERT INTO merchants (
    business_name, email, phone, location_lat, location_lon, address, city, state, zip_code,
    service_category, rating, total_reviews, photo_url, bio, years_experience, is_verified,
    yelp_id, price_range, photos, specialties, stylist_names, booking_url, data_source
) VALUES (
    'Acote Salon',
    'info@acotesalon.com',
    '+1-617-262-6200',
    42.3512, -71.0779,
    '122 Newbury Street',
    'Boston', 'MA', '02116',
    'hair_salon',
    4.9, 445,
    'https://images.unsplash.com/photo-1562322140-8baeececf3df?w=400',
    'Premier Boston salon specializing in color correction and extensions. Our artists are trained in the latest techniques and trends.',
    20, true,
    'acote-salon-boston', '$$$$',
    '["https://images.unsplash.com/photo-1562322140-8baeececf3df?w=400"]'::jsonb,
    ARRAY['Color Correction', 'Extensions', 'Textured Hair', 'Bridal'],
    ARRAY['Robert Chen', 'Nicole Adams', 'Kevin Wright', 'Laura Martinez'],
    'https://acotesalon.com/appointments',
    'yelp'
);

-- Services for Acote Salon
INSERT INTO services (merchant_id, service_name, description, base_price, duration_minutes, stylist_name, category) VALUES
((SELECT id FROM merchants WHERE business_name = 'Acote Salon'), 'Haircut', 'Precision cut with consultation', 95.00, 45, NULL, 'haircut'),
((SELECT id FROM merchants WHERE business_name = 'Acote Salon'), 'Color Correction', 'Expert color correction service', 300.00, 240, NULL, 'color'),
((SELECT id FROM merchants WHERE business_name = 'Acote Salon'), 'Brazilian Blowout', 'Smoothing keratin treatment', 375.00, 180, NULL, 'treatment');

-- ============================================================================
-- CAMBRIDGE PROVIDERS
-- ============================================================================

-- 6. Cambridge Barbershop - Classic barbershop
INSERT INTO merchants (
    business_name, email, phone, location_lat, location_lon, address, city, state, zip_code,
    service_category, rating, total_reviews, photo_url, bio, years_experience, is_verified,
    yelp_id, price_range, photos, specialties, stylist_names, booking_url, data_source
) VALUES (
    'Cambridge Barbershop',
    'info@cambridgebarbershop.com',
    '+1-617-876-7550',
    42.3876, -71.1193,
    '1728 Massachusetts Ave',
    'Cambridge', 'MA', '02138',
    'barber',
    4.9, 567,
    'https://images.unsplash.com/photo-1503951914875-452162b0f3f1?w=400',
    'Old-school barbershop with a modern twist. Expert cuts, fades, and traditional hot towel shaves. Walk-ins welcome.',
    18, true,
    'cambridge-barbershop', '$$',
    '["https://images.unsplash.com/photo-1503951914875-452162b0f3f1?w=400"]'::jsonb,
    ARRAY['Fades', 'Beard Styling', 'Classic Cuts', 'Hot Towel Shaves'],
    ARRAY['Tony Martinez', 'James Wilson', 'Chris Park', 'Mike Johnson'],
    'https://cambridgebarbershop.com/book',
    'yelp'
);

-- Services for Cambridge Barbershop
INSERT INTO services (merchant_id, service_name, description, base_price, duration_minutes, stylist_name, category) VALUES
((SELECT id FROM merchants WHERE business_name = 'Cambridge Barbershop'), 'Classic Haircut', 'Traditional scissor cut', 35.00, 30, NULL, 'haircut'),
((SELECT id FROM merchants WHERE business_name = 'Cambridge Barbershop'), 'Fade', 'Precision fade cut', 40.00, 35, NULL, 'haircut'),
((SELECT id FROM merchants WHERE business_name = 'Cambridge Barbershop'), 'Beard Trim', 'Shape and trim beard', 20.00, 15, NULL, 'beard'),
((SELECT id FROM merchants WHERE business_name = 'Cambridge Barbershop'), 'Hot Towel Shave', 'Classic straight razor shave', 35.00, 30, NULL, 'shave');

-- 7. The Beauty Spa Cambridge - Facial and waxing specialists
INSERT INTO merchants (
    business_name, email, phone, location_lat, location_lon, address, city, state, zip_code,
    service_category, rating, total_reviews, photo_url, bio, years_experience, is_verified,
    yelp_id, price_range, photos, specialties, stylist_names, booking_url, data_source
) VALUES (
    'The Beauty Spa Cambridge',
    'hello@thebeautyspacambridge.com',
    '+1-617-547-7788',
    42.3720, -71.1212,
    '57 JFK Street',
    'Cambridge', 'MA', '02138',
    'facial',
    4.7, 289,
    'https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?w=400',
    'Harvard Square destination for facials and skincare. Our estheticians provide customized treatments for all skin types.',
    10, true,
    'beauty-spa-cambridge', '$$',
    '["https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?w=400"]'::jsonb,
    ARRAY['Facials', 'Waxing', 'Skincare Consultations', 'Acne Treatment'],
    ARRAY['Maria Garcia', 'Linda Thompson', 'Rachel Green'],
    'https://thebeautyspacambridge.com/book',
    'yelp'
);

-- Services for The Beauty Spa Cambridge
INSERT INTO services (merchant_id, service_name, description, base_price, duration_minutes, stylist_name, category) VALUES
((SELECT id FROM merchants WHERE business_name = 'The Beauty Spa Cambridge'), 'Classic Facial', 'Deep cleansing facial', 95.00, 60, NULL, 'facial'),
((SELECT id FROM merchants WHERE business_name = 'The Beauty Spa Cambridge'), 'Anti-Aging Facial', 'Advanced anti-aging treatment', 145.00, 75, NULL, 'facial'),
((SELECT id FROM merchants WHERE business_name = 'The Beauty Spa Cambridge'), 'Eyebrow Waxing', 'Brow shaping and waxing', 25.00, 15, NULL, 'waxing'),
((SELECT id FROM merchants WHERE business_name = 'The Beauty Spa Cambridge'), 'Full Leg Wax', 'Complete leg waxing', 75.00, 45, NULL, 'waxing');

-- 8. Floyd's 99 Barbershop Kendall - Modern barbershop
INSERT INTO merchants (
    business_name, email, phone, location_lat, location_lon, address, city, state, zip_code,
    service_category, rating, total_reviews, photo_url, bio, years_experience, is_verified,
    yelp_id, price_range, photos, specialties, stylist_names, booking_url, data_source
) VALUES (
    'Floyd''s 99 Barbershop',
    'kendall@floydsbarbershop.com',
    '+1-617-621-1199',
    42.3663, -71.0900,
    '1 Kendall Square',
    'Cambridge', 'MA', '02139',
    'barber',
    4.5, 412,
    'https://images.unsplash.com/photo-1585747860715-2ba37e788b70?w=400',
    'Rock and roll barbershop experience. Quick, quality cuts with a cool vibe. Walk-ins always welcome.',
    5, true,
    'floyds-99-barbershop-kendall', '$$',
    '["https://images.unsplash.com/photo-1585747860715-2ba37e788b70?w=400"]'::jsonb,
    ARRAY['Quick Service', 'Modern Cuts', 'Walk-ins Welcome', 'Beard Trims'],
    ARRAY['Jake Miller', 'Brandon Lee', 'Marcus Johnson'],
    'https://floydsbarbershop.com/book',
    'yelp'
);

-- Services for Floyd's 99
INSERT INTO services (merchant_id, service_name, description, base_price, duration_minutes, stylist_name, category) VALUES
((SELECT id FROM merchants WHERE business_name = 'Floyd''s 99 Barbershop'), 'Floyd''s Haircut', 'Signature haircut with style', 32.00, 25, NULL, 'haircut'),
((SELECT id FROM merchants WHERE business_name = 'Floyd''s 99 Barbershop'), 'Beard Trim', 'Shape and clean up beard', 18.00, 15, NULL, 'beard'),
((SELECT id FROM merchants WHERE business_name = 'Floyd''s 99 Barbershop'), 'Head Shave', 'Clean head shave', 28.00, 20, NULL, 'shave');

-- 9. Dellaria Salon Cambridge - Upscale salon in Porter Square
INSERT INTO merchants (
    business_name, email, phone, location_lat, location_lon, address, city, state, zip_code,
    service_category, rating, total_reviews, photo_url, bio, years_experience, is_verified,
    yelp_id, price_range, photos, specialties, stylist_names, booking_url, data_source
) VALUES (
    'Dellaria Salon Cambridge',
    'cambridge@dellariasalons.com',
    '+1-617-868-6050',
    42.3887, -71.1191,
    '1815 Massachusetts Ave',
    'Cambridge', 'MA', '02140',
    'hair_salon',
    4.6, 356,
    'https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=400',
    'Full-service salon offering cuts, color, and spa services. Our team stays current with the latest trends and techniques.',
    30, true,
    'dellaria-salon-cambridge', '$$$',
    '["https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=400"]'::jsonb,
    ARRAY['Cuts', 'Color', 'Highlights', 'Keratin'],
    ARRAY['Patricia Lee', 'Daniel Brown', 'Sofia Martinez'],
    'https://dellariasalons.com/book',
    'yelp'
);

-- Services for Dellaria Salon
INSERT INTO services (merchant_id, service_name, description, base_price, duration_minutes, stylist_name, category) VALUES
((SELECT id FROM merchants WHERE business_name = 'Dellaria Salon Cambridge'), 'Women''s Cut', 'Haircut with blow dry', 70.00, 60, NULL, 'haircut'),
((SELECT id FROM merchants WHERE business_name = 'Dellaria Salon Cambridge'), 'Men''s Cut', 'Precision men''s haircut', 45.00, 30, NULL, 'haircut'),
((SELECT id FROM merchants WHERE business_name = 'Dellaria Salon Cambridge'), 'Single Process Color', 'All-over color application', 85.00, 90, NULL, 'color'),
((SELECT id FROM merchants WHERE business_name = 'Dellaria Salon Cambridge'), 'Partial Highlights', 'Face-framing highlights', 120.00, 90, NULL, 'color');

-- 10. Cambridge Nails & Spa - Affordable nail salon
INSERT INTO merchants (
    business_name, email, phone, location_lat, location_lon, address, city, state, zip_code,
    service_category, rating, total_reviews, photo_url, bio, years_experience, is_verified,
    yelp_id, price_range, photos, specialties, stylist_names, booking_url, data_source
) VALUES (
    'Cambridge Nails & Spa',
    'info@cambridgenailsspa.com',
    '+1-617-661-8889',
    42.3651, -71.1039,
    '424 Massachusetts Ave',
    'Cambridge', 'MA', '02139',
    'nail_salon',
    4.4, 187,
    'https://images.unsplash.com/photo-1610992015732-2449b76344bc?w=400',
    'Friendly neighborhood nail salon with affordable prices. Quick service without sacrificing quality.',
    7, true,
    'cambridge-nails-spa', '$',
    '["https://images.unsplash.com/photo-1610992015732-2449b76344bc?w=400"]'::jsonb,
    ARRAY['Quick Service', 'Affordable', 'Walk-ins Welcome'],
    ARRAY['Jenny Tran', 'Kim Nguyen'],
    'https://cambridgenailsspa.com',
    'yelp'
);

-- Services for Cambridge Nails & Spa
INSERT INTO services (merchant_id, service_name, description, base_price, duration_minutes, stylist_name, category) VALUES
((SELECT id FROM merchants WHERE business_name = 'Cambridge Nails & Spa'), 'Basic Manicure', 'Quick manicure', 18.00, 20, NULL, 'manicure'),
((SELECT id FROM merchants WHERE business_name = 'Cambridge Nails & Spa'), 'Basic Pedicure', 'Standard pedicure', 28.00, 30, NULL, 'pedicure'),
((SELECT id FROM merchants WHERE business_name = 'Cambridge Nails & Spa'), 'Gel Manicure', 'Gel polish manicure', 35.00, 35, NULL, 'manicure'),
((SELECT id FROM merchants WHERE business_name = 'Cambridge Nails & Spa'), 'Acrylic Full Set', 'Full set of acrylic nails', 45.00, 60, NULL, 'enhancement');

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Count merchants by city
SELECT city, COUNT(*) as provider_count
FROM merchants
GROUP BY city
ORDER BY city;

-- Count services per merchant
SELECT
    m.business_name,
    m.city,
    m.service_category,
    COUNT(s.id) as service_count,
    m.rating
FROM merchants m
LEFT JOIN services s ON m.id = s.merchant_id
GROUP BY m.id, m.business_name, m.city, m.service_category, m.rating
ORDER BY m.city, m.rating DESC;

-- ============================================================================
-- SUCCESS! Boston/Cambridge providers seeded
-- Expected: 10 merchants, ~40 services
-- ============================================================================
