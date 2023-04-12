#ifndef _UTILS__H_
#define _UTILS__H_ 1

#include <iomanip>
#include <sstream>
#include <string>
#include <iostream>
#include <string>
#include <algorithm>
#include <cctype>
#include <cstdio>    // For remove()
#include <fstream>   // For ifstream
#include <condition_variable>
#include <iostream>
#include <mutex>
#include <queue>


class StringUtils
{
    public:

        //
        // String operations
        //

        const static std::string toLower(const char* str);

        const static void lTrim(std::string &s);

        const static void rTrim(std::string &s);

        const static void trim(std::string &s);

        const static std::string ltrimCopy(std::string s);

        const static std::string rtrimCopy(std::string s);

        const static std::string trimCopy(std::string s);

        const static std::string to_hex_string(unsigned long n);

        const static std::string to_hex_string(unsigned int n);
        
        const static std::string to_hex_string(unsigned short n);

    private:

};

class OSUtils
{
    public:

        const static bool fileExists(const char* fileName);

        const static bool deleteFileIfExists(const char* filename);

    private:

};


template<typename T>
class TSQueue 
{
    public:
        void push(T const& value) 
        {
            std::unique_lock<std::mutex> lock(m_mutex);
            m_queue.push(value);
            lock.unlock();
            m_cond.notify_one();
        }

        bool empty() const 
        {
            std::unique_lock<std::mutex> lock(m_mutex);
            return m_queue.empty();
        }

        bool try_pop(T& popped_value) 
        {
            std::unique_lock<std::mutex> lock(m_mutex);
            if (m_queue.empty()) 
            {
                return false;
            }
            popped_value = m_queue.front();
            m_queue.pop();

            return true;
        }

        void wait_and_pop(T& popped_value) 
        {
            std::unique_lock<std::mutex> lock(m_mutex);
            while (m_queue.empty()) 
            {
                m_cond.wait(lock);
            }
            popped_value = m_queue.front();
            m_queue.pop();
        }

    private:
        std::queue<T> m_queue;
        mutable std::mutex m_mutex;
        std::condition_variable m_cond;
};


#endif // _UTILS__H_

