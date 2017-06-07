#coding:utf-8

import MySQLdb
import urllib2
import hashlib
from bs4 import BeautifulSoup

conn = MySQLdb.connect('localhost', 'root', 'root', 'test', charset='utf8')
conn.set_character_set('utf8')
cursor = conn.cursor()

# 歌手类
class Singer:
	def __init__(self, id, name, avatar, detail, hot):
		self.id = id
		self.name = name
		self.avatar = avatar
		self.detail = detail
		self.hot = hot

# 获取字符串的MD5
def getMD5(str):
	md5 = hashlib.md5()
	md5.update(str)
	return md5.hexdigest()

# 判断数据库中是否存在记录
def recordExists(singer, cursor):
	sql = "select * from singer where id = '%s'" % singer.id
	cursor.execute(sql)
	result = cursor.fetchall()
	return len(result) > 0

# 向数据库中插入一条记录
def addRecord(singer, cursor):
	sql = "insert into singer values('%s', '%s', '%s', '%s', '%s')" % (singer.id.replace("'", "''"),
		singer.name.replace("'", "''"), singer.avatar.replace("'", "''"), 
		singer.detail.replace("'", "''"), singer.hot.replace("'", "''"))
	if (not recordExists(singer, cursor)):
		try: 
			cursor.execute(sql)
			print 'insert success: %s' % singer.name
		except:
			print 'insert error: sql =', sql		
	else:
		print 'record exists: %s' % singer.name

# 获取热门歌手中带封面的部分
def getHotWithCover(doc):
	hotListWithCoverArr = doc.find(class_='hot-head clearfix').find_all('dl', recursive=False)
	for item in hotListWithCoverArr:
		aTag = item.find('dt').find('a')
		imgTag = aTag.find('img')
		singerName = imgTag['title']
		avatar = imgTag['src']
		detail = "http://music.baidu.com%s" % aTag['href']
		idStr = getMD5('%s%s' % (singerName, detail))
		print 'id =', idStr
		print 'name =', singerName
		print 'avatar =', avatar
		print 'detail =', detail
		addRecord(Singer(idStr, singerName, avatar, detail, '1'), cursor)
		print '---------------------'		

# 获取热门歌手中不带封面的部分
def getHotWithoutCover(doc):
	hotListWithoutCoverArr = doc.find('ul').find_all('li')
	for item in hotListWithoutCoverArr:
		aTag = item.find('a')
		if aTag != None:
			singerName = aTag['title']
			detail = "http://music.baidu.com%s" % aTag['href']
			idStr = getMD5('%s%s' % (singerName, detail))
			avatar = ''
			print 'id =', idStr
			print 'name =', singerName
			print 'avatar =', avatar
			print 'detail =', detail
			addRecord(Singer(idStr, singerName, avatar, detail, '0'), cursor)
			print '------------------'

# 获取按索引排列的歌手信息
def getNormalSingerInfo(doc):
	ulTag = doc.find(class_='clearfix')
	liTags = ulTag.find_all('li')
	for liTag in liTags:
		aTags = liTag.find_all('a')
		if aTags != None and len(aTags) > 0:
			aTag = aTags[0]
			singerName = aTag['title']
			detail = "http://music.baidu.com%s" % aTag['href']
			idStr = getMD5('%s%s' % (singerName, detail))
			avatar = ''
			print 'id =', idStr
			print 'name =', singerName
			print 'avatar =', avatar
			print 'detail =', detail
			addRecord(Singer(idStr, singerName, avatar, detail, '0'), cursor)
			print '------------------'

# 获取详情页的数据
def getCoverInDetailPage(singerId, detailUrl):
	print 'detail url:', detailUrl
	avatar = None
	try:
		response = urllib2.urlopen(detailUrl)
		content = response.read()
		soup = BeautifulSoup(content, 'html.parser')
		infoTag = soup.find(id='baseInfo')
		imgTag = infoTag.find(class_='cover').find('img')
		avatar = imgTag['src']
	except:
		return

	if avatar != None and avatar != '':
		sql = "update singer set avatar = '%s' where id = '%s'" % (avatar, singerId)
		try:
			cursor.execute(sql) 
			print 'update avatar success, id =', singerId
			conn.commit()
		except: 
			print 'update avatar error: sql =', sql

# 百度音乐的歌手页面：http://music.baidu.com/artist
# response = urllib2.urlopen('http://music.baidu.com/artist')
# content = response.read()
# soup = BeautifulSoup(content, 'html.parser')
# tags = soup.find(class_='container').find_all('li', recursive=False)
# 热门歌手标签
# hotListTag = tags[0]
# 热门歌手中带有封面的部分
# getHotWithCover(hotListTag)

# 热门歌手中不带封面的部分
# getHotWithoutCover(hotListTag)

# 按索引显示的歌手
# normalListTags = tags[1:len(tags)]
# for item in normalListTags:
# 	getNormalSingerInfo(item)

sql = "select * from singer where avatar = '' order by detail asc"
cursor.execute(sql)
result = cursor.fetchall()
for item in result:
	singerId = item[0]
	detailUrl = item[3]
	getCoverInDetailPage(singerId, detailUrl)

cursor.close()
conn.commit()
conn.close()