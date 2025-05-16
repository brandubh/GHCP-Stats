# Documentation Generation Instructions

I need you to generate documentation for this project following these specific requirements:

## Gounding

1. ALL THE DOCUMENTATION MUST BE GROUNDED ON @WORKSPACE CONTENTS
2. Just use source code files like .py, .sh, .bicep, .cs. DON'T use .md files or other non source code files.

## Output Format Requirements

1. Generate ALL documentation in Markdown format
2. Create SEPARATE Markdown files for each level 1 section listed below
3. Place all files in the `/docs/` directory with descriptive filenames
4. Use code blocks with syntax highlighting for all code examples
5. Implement mermaid diagrams directly in Markdown for visual representations

## For Prompt-Related Documentation

When documenting prompts:

- Include version numbers (e.g., "v1.0")
- Format templates with {placeholder} notation
- Provide explicit rationale for prompt design choices
- Include a section for tracking performance metrics
- Reference any pattern libraries or successful examples used

## Generate These Specific Documentation Files:

Generate the following separate Markdown files (skip any sections that don't apply to the current context):

1. `/docs/introduction.md` containing:
   - Purpose and scope
   - Key features and capabilities

2. `/docs/dependencies.md` containing:
   - External systems
   - Libraries and frameworks
   - Version requirements

3. `/docs/solution-overview.md` containing:
   - High-level overview
   - Core functionality explanation
   - User workflows

4. `/docs/architecture.md` containing:
   - Requirements summary
   - Component diagram (using mermaid)
   - Key software components
   - Integration points

5. `/docs/data-architecture.md` containing:
   - Data models
   - Storage solutions
   - Entity relationships (using mermaid)

6. `/docs/configuration.md` containing:
   - Environment variables
   - Configuration files
   - Deployment parameters

7. `/docs/monitoring.md` containing:
   - Logging strategy
   - Monitoring approach
   - Alert mechanisms

8. `/docs/security.md` containing:
   - Authentication methods
   - Authorization model
   - Secrets management
   - Security testing

9. `/docs/deployment.md` containing:
   - CI/CD pipeline
   - Infrastructure requirements
   - Deployment steps

10. `/docs/versioning.md` containing:
    - Current version
    - Version history
    - Upgrade notes

11. `/docs/references.md` containing:
    - Links to related documentation
    - Additional resources

For each file, include detailed content relevant to the section topic. Show me each file separately in your response, with the filename clearly indicated at the beginning of each section.
