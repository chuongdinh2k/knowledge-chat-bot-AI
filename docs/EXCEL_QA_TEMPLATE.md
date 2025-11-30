# Excel Q&A Template Guide

This guide explains how to format Excel files for Q&A (Question & Answer) ingestion.

## Supported Format

The system automatically detects Excel files with Q&A format based on column names.

### Required Columns

Your Excel file should have at least two columns:

1. **Question Column** - One of these names (case-insensitive):
   - `question`
   - `questions`
   - `q`
   - `query`
   - `queries`

2. **Answer Column** - One of these names (case-insensitive):
   - `answer`
   - `answers`
   - `a`
   - `response`
   - `responses`
   - `reply`
   - `replies`

### Example Excel Structure

| Question | Answer |
|----------|--------|
| What is Python? | Python is a high-level programming language. |
| How do I install Python? | You can install Python from python.org or using package managers. |
| What is a variable? | A variable is a container that stores data values. |

### Multiple Sheets

You can have multiple sheets in your Excel file. Each sheet will be processed separately, and the sheet name will be stored in metadata.

### Additional Columns

Any additional columns beyond Question/Answer will be stored as metadata:

| Question | Answer | Category | Difficulty |
|----------|--------|----------|------------|
| What is Python? | Python is... | Programming | Easy |
| How do I install? | You can... | Setup | Medium |

The `Category` and `Difficulty` columns will be stored in the document metadata.

## Usage

1. Create an Excel file (.xlsx or .xls) with the Q&A format
2. Upload the file using the `/api/v1/ingest/file` endpoint
3. The system will automatically detect the Q&A format and process accordingly

## Storage

Each Q&A pair is stored as a separate document in the database with:
- **Content**: Combined text "Question: {question}\nAnswer: {answer}"
- **Metadata**: Includes question, answer, sheet name, row index, and any additional columns
- **Embedding**: Vector embedding of the combined Q&A text

This allows the system to:
- Retrieve relevant Q&A pairs based on user queries
- Maintain the question-answer relationship
- Support filtering by metadata (category, difficulty, etc.)

