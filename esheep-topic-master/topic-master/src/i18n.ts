export type Language = 'zh' | 'en';

export const translations = {
  zh: {
    // Header
    appTitle: 'Topic Master 选题大师',
    themeLight: '浅色模式',
    themeDark: '深色模式',
    themeSystem: '跟随系统',
    langLabel: '中 / EN',

    // Columns
    colUnselected: '未选散落池',
    colSelected: '精选选题池',
    colInProgress: '正在制作中',
    colCompleted: '已完成/归档',

    // Column Empty & Drag
    dragCardsHere: '暂无卡片，可拖拽卡片至此',
    dropTopicHere: '释放卡片置于此处',

    // Topic Card
    sourceLink: '源链接 ↗',
    badgeHotlist: '热榜',
    badgeBenchmark: '对标',
    badgeInspiration: '灵感',
    createdDate: '创建时间',

    // Edit Modal
    editTopicTitle: '编辑选题',
    sourcePlatform: '来源平台',
    modalCreatedDate: '创建时间',
    topicTitleLabel: '选题标题',
    sourceUrlLabel: '原始链接',
    openLinkBtn: '打开链接',
    topicNotesLabel: '选题思考与笔记',
    topicNotesPlaceholder: '在此记录选题 Hook 吸睛点、切入视角与大纲笔记...',
    deleteBtn: '删除',
    cancelBtn: '取消',
    saveBtn: '保存修改',

    // Delete Zone
    deleteZoneHover: '松开即可删除',
    deleteZoneDefault: '拖至此处删除',
  },
  en: {
    // Header
    appTitle: 'Topic Master',
    themeLight: 'Light Mode',
    themeDark: 'Dark Mode',
    themeSystem: 'System Mode',
    langLabel: 'EN / 中',

    // Columns
    colUnselected: 'Unselected Topics',
    colSelected: 'Selected Topics',
    colInProgress: 'In Progress',
    colCompleted: 'Completed',

    // Column Empty & Drag
    dragCardsHere: 'Drag cards here',
    dropTopicHere: 'Drop topic here',

    // Topic Card
    sourceLink: 'Source ↗',
    badgeHotlist: 'Hotlist',
    badgeBenchmark: 'Benchmark',
    badgeInspiration: 'Inspiration',
    createdDate: 'Created Date',

    // Edit Modal
    editTopicTitle: 'Edit Topic',
    sourcePlatform: 'Source Platform',
    modalCreatedDate: 'Created Date',
    topicTitleLabel: 'Topic Title',
    sourceUrlLabel: 'Source URL',
    openLinkBtn: 'Open Link',
    topicNotesLabel: 'Topic Notes & Outline',
    topicNotesPlaceholder: 'Record topic hooks, angles, script outline, and notes here...',
    deleteBtn: 'Delete',
    cancelBtn: 'Cancel',
    saveBtn: 'Save Changes',

    // Delete Zone
    deleteZoneHover: 'Release to Delete',
    deleteZoneDefault: 'Drag Here to Delete',
  },
};
