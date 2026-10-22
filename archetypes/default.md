+++
date = '{{ .Date }}'
draft = true
title = '{{ replace .File.ContentBaseName "-" " " | title }}'
# 可选：featured = true 即进入首页「精选文章」区（未声明 = 非精选；
#       只认布尔 true，写成字符串会让构建失败。见 CONTEXT.md「精选」）
+++
