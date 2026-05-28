export type AgentChannelKind = 'im'

export interface AgentChannelListRow {
  id: string
  name: string
  kind: AgentChannelKind
  kindLabel: string
  status: 'connected' | 'disabled' | 'enabled'
  statusLabel: string
  userScaleLabel: string
  action: 'configure' | 'onboard'
  actionLabel: string
}

export const DEMO_AGENT_CHANNELS: AgentChannelListRow[] = [
  {
    id: 'telegram',
    name: 'Telegram',
    kind: 'im',
    kindLabel: 'IM',
    status: 'connected',
    statusLabel: '已接入',
    userScaleLabel: '2,301',
    action: 'configure',
    actionLabel: '配置',
  },
  {
    id: 'discord',
    name: 'Discord',
    kind: 'im',
    kindLabel: 'IM',
    status: 'disabled',
    statusLabel: '未接入',
    userScaleLabel: '—',
    action: 'onboard',
    actionLabel: '接入',
  },
  {
    id: 'whatsapp',
    name: 'WhatsApp',
    kind: 'im',
    kindLabel: 'IM',
    status: 'disabled',
    statusLabel: '未接入',
    userScaleLabel: '—',
    action: 'onboard',
    actionLabel: '接入',
  },
]
