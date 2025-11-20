-- ============================================================================
-- GlowGo Enhanced Merchant Fields Migration
-- For Real Provider Data from Yelp API and BrightData Scraping
-- ============================================================================
--
-- Instructions:
-- 1. Open Supabase Dashboard → SQL Editor
-- 2. Run this migration to add enhanced fields for real provider data
--
-- ============================================================================

-- Add new columns to merchants table for enhanced provider data
ALTER TABLE merchants ADD COLUMN IF NOT EXISTS yelp_id VARCHAR(255) UNIQUE;
ALTER TABLE merchants ADD COLUMN IF NOT EXISTS google_place_id VARCHAR(255);
ALTER TABLE merchants ADD COLUMN IF NOT EXISTS website VARCHAR(500);
ALTER TABLE merchants ADD COLUMN IF NOT EXISTS yelp_url VARCHAR(500);
ALTER TABLE merchants ADD COLUMN IF NOT EXISTS price_range VARCHAR(10); -- $, $$, $$$, $$$$
ALTER TABLE merchants ADD COLUMN IF NOT EXISTS review_count INTEGER DEFAULT 0;
ALTER TABLE merchants ADD COLUMN IF NOT EXISTS photos JSONB DEFAULT '[]'::jsonb; -- Array of photo URLs
ALTER TABLE merchants ADD COLUMN IF NOT EXISTS business_hours JSONB; -- Operating hours by day
ALTER TABLE merchants ADD COLUMN IF NOT EXISTS categories JSONB DEFAULT '[]'::jsonb; -- Yelp categories
ALTER TABLE merchants ADD COLUMN IF NOT EXISTS specialties TEXT[]; -- Array of specialties
ALTER TABLE merchants ADD COLUMN IF NOT EXISTS stylist_names TEXT[]; -- Array of stylist names
ALTER TABLE merchants ADD COLUMN IF NOT EXISTS accepts_walkins BOOLEAN DEFAULT false;
ALTER TABLE merchants ADD COLUMN IF NOT EXISTS booking_url VARCHAR(500); -- Direct booking link
ALTER TABLE merchants ADD COLUMN IF NOT EXISTS data_source VARCHAR(50) DEFAULT 'manual'; -- yelp, brightdata, manual
ALTER TABLE merchants ADD COLUMN IF NOT EXISTS last_scraped_at TIMESTAMP WITH TIME ZONE;

-- Add indexes for new columns
CREATE INDEX IF NOT EXISTS idx_merchants_yelp_id ON merchants(yelp_id);
CREATE INDEX IF NOT EXISTS idx_merchants_data_source ON merchants(data_source);
CREATE INDEX IF NOT EXISTS idx_merchants_price_range ON merchants(price_range);

-- Add enhanced fields to services table
ALTER TABLE services ADD COLUMN IF NOT EXISTS stylist_name VARCHAR(255);
ALTER TABLE services ADD COLUMN IF NOT EXISTS category VARCHAR(100);
ALTER TABLE services ADD COLUMN IF NOT EXISTS subcategory VARCHAR(100);
ALTER TABLE services ADD COLUMN IF NOT EXISTS price_varies BOOLEAN DEFAULT false;
ALTER TABLE services ADD COLUMN IF NOT EXISTS price_min DECIMAL(10, 2);
ALTER TABLE services ADD COLUMN IF NOT EXISTS price_max DECIMAL(10, 2);

-- Create availability_slots table for real-time availability tracking
CREATE TABLE IF NOT EXISTS availability_slots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL REFERENCES merchants(id) ON DELETE CASCADE,
    service_id UUID REFERENCES services(id) ON DELETE CASCADE,
    stylist_name VARCHAR(255),
    slot_date DATE NOT NULL,
    slot_time_start TIME NOT NULL,
    slot_time_end TIME NOT NULL,
    is_available BOOLEAN DEFAULT true,
    scraped_from VARCHAR(100), -- styleseat, booksy, vagaro, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for availability_slots
CREATE INDEX IF NOT EXISTS idx_availability_merchant_id ON availability_slots(merchant_id);
CREATE INDEX IF NOT EXISTS idx_availability_slot_date ON availability_slots(slot_date);
CREATE INDEX IF NOT EXISTS idx_availability_is_available ON availability_slots(is_available);
CREATE INDEX IF NOT EXISTS idx_availability_stylist ON availability_slots(stylist_name);

-- Trigger for availability_slots updated_at
CREATE TRIGGER update_availability_slots_updated_at BEFORE UPDATE ON availability_slots
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create data_collection_logs table for tracking scraping jobs
CREATE TABLE IF NOT EXISTS data_collection_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_type VARCHAR(50) NOT NULL, -- yelp_search, brightdata_scrape, etc.
    location VARCHAR(255), -- Boston, Cambridge, etc.
    search_term VARCHAR(255), -- hair salon, massage, etc.
    results_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Index for data_collection_logs
CREATE INDEX IF NOT EXISTS idx_collection_logs_status ON data_collection_logs(status);
CREATE INDEX IF NOT EXISTS idx_collection_logs_job_type ON data_collection_logs(job_type);

-- ============================================================================
-- Update service_category constraint to include more beauty services
-- ============================================================================

-- First, drop the existing constraint
ALTER TABLE merchants DROP CONSTRAINT IF EXISTS merchants_service_category_check;

-- Add new constraint with expanded categories
ALTER TABLE merchants ADD CONSTRAINT merchants_service_category_check
    CHECK (service_category IN (
        'haircut', 'hair_salon', 'barber',
        'nails', 'nail_salon',
        'massage', 'massage_therapy',
        'spa', 'day_spa', 'med_spa',
        'facial', 'skincare', 'esthetician',
        'waxing', 'hair_removal',
        'makeup', 'beauty',
        'eyebrows', 'eyelashes', 'brows_lashes',
        'tanning',
        'other'
    ));

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Check that new columns were added
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'merchants'
AND column_name IN ('yelp_id', 'photos', 'business_hours', 'price_range', 'specialties');

-- Check availability_slots table exists
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name = 'availability_slots';

-- Check data_collection_logs table exists
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name = 'data_collection_logs';

-- ============================================================================
-- SUCCESS! Enhanced fields added for real provider data
-- ============================================================================
