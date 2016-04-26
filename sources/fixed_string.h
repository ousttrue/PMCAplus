#pragma once

template<int N>
class fixed_string
{
	static_assert(N > 0, "0 size");
	char m_str[N + 1];

public:
	fixed_string()
	{
		memset(m_str, 0, sizeof(m_str));
	}

	fixed_string(const fixed_string &src)
	{
		*this = src.c_str();
	}

	fixed_string(const char *src)
	{
		*this = src;
	}

	fixed_string& operator=(const std::string &src)
	{
		*this = src.c_str();
		return *this;
	}

	fixed_string& operator=(const char *src)
	{
		for (int i = 0; i < N; ++i) {
			m_str[i] = src[i];
			if (m_str[i] == '\0') {
				break;
			}
		}
		return *this;
	}

	bool operator==(const fixed_string &src)const
	{
		if (this == &src)return true;
		return *this == src.c_str();
	}

	bool operator==(const std::string &src)const
	{
		return *this == src.c_str();
	}

	bool operator==(const char *src)const
	{
		for (int i = 0; i < N; ++i) {
			if (m_str[i] != src[i]) {
				return false;
			}
			if (m_str[i] == '\0')break;
		}
		return true;
	}

	int capacity()const { return N; }

	int size()const {
		int i = 0;
		for (; i < N; ++i) {
			if (m_str[i] == '\0') {
				break;
			}
		}
		return i;
	}

	void clear()
	{
		m_str[0] = '\0';
	}

	char* data() { return m_str; }
	const char *c_str()const { return m_str; }

	bool is_trim(char c)
	{
		switch (c)
		{
		case '\n':
			return true;

		default:
			return false;
		}
	}

	template<int M>
	int fread(FILE *fp)
	{
		char buf[M];
		int m = ::fread(buf, 1, M, fp);
		int i = 0;
		for (; i < std::min(N, m); ++i)
		{
			m_str[i] = buf[i];
			if (m_str[i] == '\0') {
				break;
			}
		}
		for (int j = i; j < N; ++j) {
			m_str[j] = '\0';
		}
		for (int j = i - 1; j >= 0; --j) {
			if (is_trim(m_str[j])) {
				m_str[j] = '\0';
				continue;
			}
			return j + 1;
		}
		return 0;
	}
};
