# GitHub Actions Workflows

## Monthly Analysis Workflow

The `monthly-analysis.yml` workflow automatically runs the Million Dollar Homepage analyzer on the 1st of each month at 12:00 UTC.

### What it does:

1. **Scheduled Execution**: Runs monthly on the 1st at 12:00 UTC (can be manually triggered as well)
2. **Environment Setup**: Sets up Python 3.9 and installs dependencies
3. **Analysis**: Downloads the current Million Dollar Homepage and extracts pixel data
4. **Data Storage**: Saves the analysis results to the `data/` folder
5. **Version Control**: Commits and pushes the new data file to the repository

### Output:

Each run generates a timestamped JSON file in the `data/` folder with the format:
```
data/pixel_data_YYYYMMDD_HHMMSS.json
```

### Manual Triggering:

You can manually trigger the workflow from the GitHub Actions tab in your repository by clicking "Run workflow" on the "Monthly Million Dollar Homepage Analysis" workflow.

### Configuration:

- **Schedule**: Modify the cron expression in the workflow file to change the execution time
- **Python Version**: Currently uses Python 3.9 (can be updated in the workflow)
- **Output Directory**: Files are saved to the `data/` folder by default

### Monitoring:

Check the Actions tab in your GitHub repository to monitor workflow runs and view logs.