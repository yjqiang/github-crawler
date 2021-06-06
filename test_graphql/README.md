1. [The difference between v3 and v4 is fundamental: v3 is RESTful, while v4 uses Facebook's GraphQL paradigm.](https://www.reddit.com/r/github/comments/bny3yp/github_api_v3_vs_v4_for_java/)
1. If we look at the general structure of the common connection implementation you typically have the following:  
   TypeA -> TypeAToTypeBConnection (usually a field on TypeA with a name like `typeBConnection`) -> TypeAToTypeBEdge (usually field of name on connection with name `edges`) -> TypeB (usually field name on an edge with name `node`)
   ```
   A -> connection -> edges -> B
   ```
   `Connection types` will normally have fields containing information which is specific to the entire connection which is typicall `pageInfo`, `totalCount`, etc.  
   `Edge types` normally have fields which have information which is specific to that connection but not common to all nodes. The most common field in this case is `cursor` which represents the nodes **location** in the connection which is not a globally unique ID but a way to return to that location in the connection.  
   `Node type` is normally just the type which the connection goes too which contains no connection specific information.  
1. 举例
    ```
    repository(owner:"aio-libs", name:"aiohttp") {  # https://docs.github.com/en/graphql/reference/queries#repository  
                                                    # 查找 Repository 这个 object，拥有 name、owner 这些 Arguments
        issues(last:20) { # Repository 这个 object 有 issue 这个 Fields，issue 拥有 last、states 这些 Arguments
                                         # 这里 issues 的 type 是 IssueConnection
            edges {   #  Every `edges` field has a `node` field and a `cursor` field. cursor 可以用于 分页
                      # 这里 edges 的 type 是 IssueEdge
                node {  # Node type is normally just the type which the connection goes to which contains no connection specific information
                        # we specify the `title`, `url`, and `labels` fields of the Issue object.
                        # 这里 node 的 type 是 Issue
                        
                    title
                    url
                    labels(first:5) {  # 这里 labels 的 type 是 LabelConnection，拥有 first 这些 Arguments
                        edges { # 这里 edges 的 type 是 LabelEdge
                            node {  # 这里 node 的 type 是 Label
                                name
                                pullRequests {totalCount}
                            }
                        }
                    }
                }
                cursor
            }
        }
    }
    ```
1. 有一个需求，需要获取当前账号的名字，url，签名，加入Github的时间，邮箱，以及该账号的前5个followers（账号名、bio、邮箱、加入Github的时间），当前账号的前5个仓库（名字、star信息、fork信息），下面是构造出来的GraphQL查询语句
    ```
   query {
      viewer {  # https://docs.github.com/en/graphql/reference/queries#user
         login
         url
         bio
         email
         createdAt
         followers(first : 5) {
            edges {
               node {
                  name
                  bio
                  email
                  createdAt
               }
            }
         }
         repositories(first : 5, isFork : false) {
            edges {
               node {
                  name
                  stargazers (first : 10){
                     edges {
                        starredAt
                        node {
                           name
                        }
                     }
                  }
                  forks (first : 10){
                     edges {
                        node {
                           createdAt
                           name
                        }
                     }
                  }
               }
            }
         }
      }
   }
    ```
1. 坑:
   1. [No support for code searches using the GraphQL v4 API.](https://stackoverflow.com/questions/45382069/search-for-code-in-github-using-graphql-v4-api]