#ifndef _UTILS__H_
#define _UTILS__H_ 1

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

    private:

};

class OSUtils
{
    public:

        const static bool fileExists(const char* fileName);

        const static bool deleteFileIfExists(const char* filename);

    private:

};


// Thread-safe queue
template <typename T>
class TSQueue 
{

	public:

        // Pushes an element to the queue
        void push(T item)
        {
    
            // Acquire lock
            std::unique_lock<std::mutex> lock(m_mutex);
    
            // Add item
            m_queue.push(item);
    
            // Notify one thread that
            // is waiting
            m_cond.notify_one();
        }
    
        // Pops an element off the queue
        T pop()
        {
    
            // acquire lock
            std::unique_lock<std::mutex> lock(m_mutex);
    
            // wait until queue is not empty
            m_cond.wait(lock,
                        [this]() { return !m_queue.empty(); });
    
            // retrieve item
            T item = m_queue.front();
            m_queue.pop();
    
            // return item
            return item;
        }

	private:
		// Underlying queue
		std::queue<T> m_queue;
	  
		// mutex for thread synchronization
		std::mutex m_mutex;
	  
		// Condition variable for signaling
		std::condition_variable m_cond;        
};
  



#endif // _UTILS__H_

