// Settings scoped to the isolated Qwen3.6 MTP provider.
export default async () => ({
  "chat.params": async (input: any, output: any) => {
    if (["llamacpp-mtp", "llamacpp-mtp2", "llamacpp-dflash4"].includes(input.model.providerID)) {
      output.maxOutputTokens = 32768
      output.temperature = 0.6
      output.topP = 0.95
    }
  },
})
