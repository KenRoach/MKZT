-- Create AI results table
CREATE TABLE IF NOT EXISTS ai_results (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    task TEXT NOT NULL,
    input_text TEXT NOT NULL,
    result JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create transcripts table
CREATE TABLE IF NOT EXISTS transcripts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    transcript TEXT NOT NULL,
    language TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create sentiments table
CREATE TABLE IF NOT EXISTS sentiments (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    text TEXT NOT NULL,
    score FLOAT NOT NULL,
    magnitude FLOAT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_ai_results_task ON ai_results(task);
CREATE INDEX IF NOT EXISTS idx_ai_results_created_at ON ai_results(created_at);
CREATE INDEX IF NOT EXISTS idx_transcripts_language ON transcripts(language);
CREATE INDEX IF NOT EXISTS idx_transcripts_created_at ON transcripts(created_at);
CREATE INDEX IF NOT EXISTS idx_sentiments_created_at ON sentiments(created_at);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_ai_results_updated_at
    BEFORE UPDATE ON ai_results
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_transcripts_updated_at
    BEFORE UPDATE ON transcripts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sentiments_updated_at
    BEFORE UPDATE ON sentiments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create RLS policies
ALTER TABLE ai_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE transcripts ENABLE ROW LEVEL SECURITY;
ALTER TABLE sentiments ENABLE ROW LEVEL SECURITY;

-- Create policies for authenticated users
CREATE POLICY "Allow authenticated users to read ai_results"
    ON ai_results FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Allow authenticated users to insert ai_results"
    ON ai_results FOR INSERT
    TO authenticated
    WITH CHECK (true);

CREATE POLICY "Allow authenticated users to read transcripts"
    ON transcripts FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Allow authenticated users to insert transcripts"
    ON transcripts FOR INSERT
    TO authenticated
    WITH CHECK (true);

CREATE POLICY "Allow authenticated users to read sentiments"
    ON sentiments FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Allow authenticated users to insert sentiments"
    ON sentiments FOR INSERT
    TO authenticated
    WITH CHECK (true); 