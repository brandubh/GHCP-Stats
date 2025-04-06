
- No lines of code manually written
  - Manual intervention would have cut times even more
- Better one shot generation than getting to the complete code step by step
- better focus generation on a spcecific framework
- use copilot-instrcutions.md to set your workspace rules
- enable [experimantal feature](https://code.visualstudio.com/docs/copilot/copilot-customization#_reusable-prompt-files-experimental) to have a prompts library to reference in chat
- while o3-mini has the best score in coding, I got on average better results with Sonnet 3.7
  - Be ready to switch models based on the task to be acomplished
- Documentation generation is prone to hallucinations if using @workspace or @github, grounding on specific files performs better?
