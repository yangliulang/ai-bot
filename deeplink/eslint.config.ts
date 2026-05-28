import { globalIgnores } from 'eslint/config'
import { defineConfigWithVueTs, vueTsConfigs } from '@vue/eslint-config-typescript'
import pluginVue from 'eslint-plugin-vue'
import skipFormatting from 'eslint-config-prettier/flat'

export default defineConfigWithVueTs(
  {
    name: 'deeplink/app',
    files: ['**/*.{vue,ts}'],
  },
  globalIgnores(['**/dist/**', '**/node_modules/**']),
  ...pluginVue.configs['flat/essential'],
  vueTsConfigs.recommended,
  skipFormatting,
)
