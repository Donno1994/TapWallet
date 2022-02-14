def shortenHexString(longString,mediumLength=False):

	a=8
	b=-5
	if mediumLength:a=14;b=-11
	shortString=longString[:a]
	shortString+="....."
	shortString+=longString[b:]
	return shortString
