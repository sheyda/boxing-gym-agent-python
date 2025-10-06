Testing edge cases:

# Short OpenAI key (should not match legacy pattern - needs 20+ chars)
OPENAI_KEY=sk-1234567890

# Partial matches (should not match)
PARTIAL_KEY=sk-proj
PARTIAL_GOOGLE=GOCSPX
PARTIAL_GMAIL=ya29

# Similar but different patterns
NOT_OPENAI=sk-other-1234567890abcdefghijklmnopqrstuvwxyz
NOT_GMAIL=ya30.a0AQQ_BDT-_6nXsc8Mbaz-TEyaMtJp456BYApuOUiSVclAs02gF4RCVU

# Safe examples
EXAMPLE_API_KEY=your-api-key-here
EXAMPLE_CLIENT_ID=your-client-id-here
EXAMPLE_TOKEN=your-token-here
