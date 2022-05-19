def shortenHexString(longString,length_a=8,length_b=5):

	a=length_a
	b=-length_b
	shortString=longString[:a]
	shortString+="....."
	shortString+=longString[b:]
	return shortString
